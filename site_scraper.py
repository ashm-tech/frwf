import asyncio
import logging
import concurrent
from concurrent.futures import ThreadPoolExecutor

import faust
from sqlalchemy import text
from scrapy.crawler import CrawlerProcess
from sqlalchemy.ext.asyncio import create_async_engine

# Project
from config import settings, log_config
from spiders import spiders_map

# init logging
logger = logging.getLogger(__name__)

thread_pool = ThreadPoolExecutor(max_workers=1)


# models
class MessageKey(faust.Record, serializer="json"):
    store_alias: str


class MessageValue(faust.Record, serializer="json"):
    message_id: str
    table_name: str
    version_value: str
    store_id: str


# faust application initialization
app = faust.App(
    settings.SC_APP_NAME,
    broker=f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
    value_serializer="raw",
    logging_config=log_config,
)

# kafka topic declaration
incoming_scrape_task_topic = app.topic(
    settings.SC_TOPIC_NAME,
    key_type=MessageKey,
    value_type=MessageValue,
    partitions=settings.SC_PARTITIONS,
)

result_topic = app.topic(
    settings.SCR_TOPIC_NAME,
    partitions=settings.SCR_PARTITIONS,
)
es_upload_topic = app.topic(
    settings.ELUP_TOPIC_NAME,
    partitions=settings.ELUP_PARTITIONS,
)
image_download_task_topic = app.topic(
    settings.ID_TOPIC_NAME,
    partitions=settings.ID_PARTITIONS,
)


def run_scrappy(config):
    logger.info(f"Run scrape with config: {config}")
    process = CrawlerProcess(
        settings={
            "ITEM_PIPELINES": {
                "spiders.pipelines.ItemSavePipeline": 300,
            },
            "CONCURRENT_REQUESTS": 256,
            "external_configs": {
                "store_alias": f"{config.get('store_alias')}",
                "table_name": config.get("table_name"),
                "store_id": config.get("store_id"),
                "version": config.get("version_value"),
                "maximum_parsing_pages": settings.SC_MAXIMUM_PARSING_PAGES,
            },
        }
    )
    spider = spiders_map[config.get("store_alias")]
    process.crawl(spider)
    process.start()


@app.agent(incoming_scrape_task_topic, concurrency=settings.SC_CONCURRENCY)
async def scrape_store(stream) -> None:
    async for msg_key, msg_value in stream.items():  # type: MessageKey, MessageValue
        logger.info(f"scrape_store received message with key: {msg_key} and value: {msg_value}")
        db_engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
        )
        try:
            # collect and store data from site to PG DB
            config = {
                "store_alias": msg_key.store_alias,
                "table_name": msg_value.table_name,
                "store_id": msg_value.store_id,
                "version_value": msg_value.version_value,
            }
            logger.info(f"ready for scrape")
            loop = asyncio.get_running_loop()
            with concurrent.futures.ProcessPoolExecutor() as pool:
                await loop.run_in_executor(pool, run_scrappy, config)
            logger.info(f"Finish scrape")
            async with db_engine.connect() as connection:
                await connection.execute(
                    text(
                        f"""
                        UPDATE frwf_service_tasks
                        SET state='DONE'
                        WHERE record_id = '{msg_value.message_id}';
                        """
                    )
                )
                await connection.commit()
                logging.info(f"Task record with record_id: {msg_value.message_id} was updated as DONE.")
        finally:
            # for AsyncEngine created in function scope, close and clean-up pooled connections
            await db_engine.dispose()
