import logging

import faust
from sqlalchemy import text
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from sqlalchemy.ext.asyncio import create_async_engine

# Project
from config import settings, log_config

# init logging
logger = logging.getLogger(__name__)


# models
class MessageKey(faust.Record, serializer="json"):
    store_alias: str


class MessageValue(faust.Record, serializer="json"):
    message_id: str
    table_name: str


# faust application initialization
app = faust.App(
    settings.ELUP_APP_NAME,
    broker=f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
    value_serializer="raw",
    logging_config=log_config,
)

# kafka topic declaration
elastic_upload_task_topic = app.topic(
    settings.ELUP_TOPIC_NAME,
    key_type=MessageKey,
    value_type=MessageValue,
    partitions=settings.ELUP_PARTITIONS,
)

result_topic = app.topic(
    settings.SCR_TOPIC_NAME,
    partitions=settings.SCR_PARTITIONS,
)


@app.agent(elastic_upload_task_topic, concurrency=settings.ELUP_CONCURRENCY)
async def elastic_upload(stream) -> None:
    async for msg_key, msg_value in stream.items():  # type: MessageKey, MessageValue
        logger.info(f"elastic_upload received message with key: {msg_key} and value: {msg_value}")
        es_url = f"https://elastic:{settings.ELASTIC_PASSWORD}@{settings.ES_HOST}:{settings.ES_PORT}"
        es = AsyncElasticsearch(hosts=[es_url], verify_certs=False)
        _, _, store_alias, version_date, version_number = msg_value.table_name.split("_")
        version = f"{version_date}_{version_number}"
        index_name = f"{store_alias}_{version}"

        db_engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
        )
        try:
            # create new index
            await es.indices.create(index=index_name)
            # get values from PG DB and put its to es
            async with db_engine.connect() as connection:
                query = await connection.execute(
                    text(
                        f"""
                        SELECT good_id, store_id, name, price, image_url, source_url
                        FROM {msg_value.table_name};
                        """
                    )
                )
                items = query.fetchall()
            logger.info(f"Total items: {len(items)} selected")
            if items:
                indices = await es.indices.get_alias()
                if index_name in indices:
                    logger.info(f"Required to delete old index: {index_name}")
                    await es.indices.delete(index=index_name)
                    logger.info(f"Index {index_name} was deleted.")
                await es.indices.create(
                    index=index_name,
                    settings={
                        "analysis": {
                            "analyzer": {"default": {"type": "russian"}, "default_search": {"type": "russian"}}
                        }
                    },
                )
                logger.info(f"Index {index_name} was created.")
                # store item to elastic
                await async_bulk(
                    client=es,
                    actions=[
                        {
                            "_index": index_name,
                            "good_id": item[0],
                            "store_id": item[1],
                            "name": item[2],
                            "price": item[3],
                            "image_url": item[4],
                            "source_url": item[5],
                        }
                        for item in items
                    ],
                )
                logger.info(f"item wa uploaded to elastic")
                # switch index, if necessary
                idx: str
                indices_for_deletion = [
                    idx for idx in indices.keys() if idx.startswith(store_alias) and idx != index_name
                ]
                await es.indices.update_aliases(
                    actions=[
                        {"add": {"index": index_name, "alias": store_alias}},
                        *[{"remove": {"index": idx_name, "alias": store_alias}} for idx_name in indices_for_deletion],
                    ]
                )
                logger.info(f"Indices was switched")
                if indices_for_deletion:
                    await es.indices.delete(index=indices_for_deletion)
                    logger.info(f"indices {indices_for_deletion} was deleted.")
            else:
                logger.info(f"No items select -> mark task done and quit.")
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
            await db_engine.dispose()
