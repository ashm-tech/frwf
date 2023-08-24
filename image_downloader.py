import io
import uuid
import logging
from ssl import SSLCertVerificationError
from asyncio import Semaphore, gather, ensure_future
from datetime import datetime

import faust
import requests
from aiohttp import ClientSession
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Project
from utils import S3Uploader, S3BucketConfig, compact
from config import settings, log_config

# init logging
logger = logging.getLogger(__name__)

semaphore = 50


# models
class MessageKey(faust.Record, serializer="json"):
    store_alias: str


class MessageValue(faust.Record, serializer="json"):
    message_id: str
    table_name: str


# faust application initialization
app = faust.App(
    settings.ID_APP_NAME,
    broker=f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
    value_serializer="raw",
    logging_config=log_config,
)

# kafka topic declaration
image_download_task_topic = app.topic(
    settings.ID_TOPIC_NAME,
    key_type=MessageKey,
    value_type=MessageValue,
    partitions=settings.ID_PARTITIONS,
)


def download_url(url) -> str:
    cfg: S3BucketConfig = settings.AWS_BUCKETS["img"]
    relative_path = url.replace(cfg.bucket_url, "")
    logger.info(f"relative path: {cfg.bucket_url, relative_path}")

    uploader = S3Uploader(conn_cfg=cfg)
    result = uploader.generate_presigned_url(relative_path, expires_in=None)
    logger.info(f"pre-signed url generated: {result}")
    return result


async def download(items, table_name, db_engine):
    tasks = list()
    sem = Semaphore(semaphore)
    conn_cfg = settings.AWS_BUCKETS["img"]
    logger.info(f"conn_cfg: {conn_cfg}")
    uploader = S3Uploader(conn_cfg=conn_cfg)
    async with ClientSession() as session:
        for good_id, url in items:
            # cose some urls contains cyrillic symbols and stores as \xd0, so revert its to normal state
            url = url.encode("utf-8", errors="ignore").decode("utf-8")
            tasks.append(
                ensure_future(
                    download_one(
                        uploader=uploader,
                        good_id=good_id,
                        url=url,
                        session=session,
                        sem=sem,
                        table_name=table_name,
                        db_engine=db_engine,
                    )
                )
            )
        return await gather(*tasks)


async def get_image_by_url(uploader, good_id, url, session, table_name, db_engine, verify_ssl=True):
    async with session.get(url, verify_ssl=verify_ssl) as response:
        content = await response.read()

        if response.status != 200:
            logger.info(f"Scraping {url} failed due to the return code {response.status}")
            return

        logger.info(f"Scraping {url} succeeded")
        # upload file to S3
        attachment_id = uuid.uuid4()
        file_ext = url.split(".")[-1]
        final_file_name = ".".join(compact(str(attachment_id), file_ext))
        folder_time_slot = datetime.now().strftime("%Y%d%m_%H%M")
        relative_path = f"{folder_time_slot}/{table_name}/{final_file_name}"
        mime_type = response.content_type
        logger.info(f"Ready to store image to minio")
        url = uploader.put_object(
            body=io.BytesIO(content),
            relative_path=relative_path,
            file_type=mime_type,
            private=False,
        )
        # store result to PG DB
        async with db_engine.connect() as db_connection:
            await db_connection.execute(
                text(
                    f"""
                            UPDATE {table_name}
                            SET image_url = '{url}'
                            WHERE good_id = '{good_id}';
                            """
                )
            )
            await db_connection.commit()


async def download_one(uploader, good_id, url, session, sem, table_name, db_engine):
    async with sem:
        try:
            await get_image_by_url(uploader, good_id, url, session, table_name, db_engine)
        except SSLCertVerificationError as e:
            # try to get image without ssl
            logger.info(f"Got SSLCertVerificationError: {e} when get url: {url}. Will try get without ssl")
            await get_image_by_url(uploader, good_id, url, session, table_name, db_engine, verify_ssl=False)
        except Exception as e:
            logger.error(
                f"Failed when try download image for good "
                f"with good_id: {good_id}, url: {url}, table_name: {table_name}, e: {e}"
            )
            raise e


@app.agent(image_download_task_topic, concurrency=settings.ID_CONCURRENCY)
async def image_download(stream) -> None:
    async for msg_key, msg_value in stream.items():  # type: MessageKey, MessageValue
        logger.info(f"image_download received message with key: {msg_key} and value: {msg_value}")
        db_engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=True,
        )
        try:
            # get values from PG DB
            async with db_engine.connect() as connection:
                query = await connection.execute(
                    text(
                        f"""
                        SELECT good_id, image_external_url 
                        FROM {msg_value.table_name}
                        WHERE image_url IS NULL;
                        """
                    )
                )
                items = query.fetchall()
            logger.info(f"Get {len(items)} items.")
            # download images
            await download(items, msg_value.table_name, db_engine)
            logger.info(f"Images was downloaded.")
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
