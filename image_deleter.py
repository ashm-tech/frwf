import io
import json
import uuid
import logging
from asyncio import Semaphore, gather, ensure_future
from datetime import datetime

import faust
from aiohttp import ClientSession
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Project
from utils import S3Uploader, S3BucketConfig, compact
from config import settings, log_config

# init logging
logger = logging.getLogger(__name__)

semaphore = 100


# models
class MessageKey(faust.Record, serializer="json"):
    store_alias: str


class MessageValue(faust.Record, serializer="json"):
    message_id: str
    table_names: str


# faust application initialization
app = faust.App(
    settings.ID_APP_NAME,
    broker=f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
    value_serializer="raw",
    logging_config=log_config,
)

# kafka topic declaration
image_delete_task_topic = app.topic(
    settings.DI_TOPIC_NAME,
    key_type=MessageKey,
    value_type=MessageValue,
    partitions=settings.DI_PARTITIONS,
)


@app.agent(image_delete_task_topic, concurrency=settings.DI_CONCURRENCY)
async def image_delete(stream) -> None:
    async for msg_key, msg_value in stream.items():  # type: MessageKey, MessageValue
        logger.info(f"image_delete received message with key: {msg_key} and value: {msg_value}")
        db_engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
        )
        try:
            cfg: S3BucketConfig = settings.AWS_BUCKETS["img"]
            bucket_url = cfg.bucket_url
            uploader = S3Uploader(conn_cfg=cfg)
            # get values from PG DB
            table_names = json.loads(msg_value.table_names)
            async with db_engine.connect() as connection:
                for table_name in table_names:
                    query = await connection.execute(
                        text(
                            f"""
                            SELECT image_url 
                            FROM {table_name}
                            WHERE image_url IS NOT NULL;
                            """
                        )
                    )
                    items = query.fetchall()
                    logger.info(f"Get {len(items)} items for table_name: {table_name}")
                    # delete images
                    for (image_url,) in items:
                        relative_path = image_url.replace(bucket_url, "")
                        uploader.delete_object(relative_path)

                logger.info(f"Images was deleted.")
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
