import logging

import psycopg2
from furl import furl
from scrapy.exceptions import DropItem

# Project
from config import settings

logger = logging.getLogger(__name__)


class ItemSavePipeline:
    store_alias: str
    table_name: str
    store_id: str
    version: str

    def open_spider(self, spider):
        logger.info(f"spider was opened")
        # called when the spider is opened
        self.store_alias = spider.settings["external_configs"]["store_alias"]
        self.table_name = spider.settings["external_configs"]["table_name"]
        self.store_id = spider.settings["external_configs"]["store_id"]
        self.version = spider.settings["external_configs"]["version"]
        self.conn = psycopg2.connect(
            database=settings.FRWF_POSTGRES_DB_NAME,
            host=settings.FRWF_POSTGRES_HOST,
            user=settings.FRWF_POSTGRES_USER,
            password=settings.FRWF_POSTGRES_PASSWORD,
            port=settings.FRWF_POSTGRES_PORT,
        )
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        logger.info(f"spider was closed")
        # called when the spider is closed
        self.conn.close()

    def process_item(self, item, spider):
        logger.debug(f"process_item: {item}")
        # called for each crawled item
        # insert the each crawled item into DB
        if not item.get("is_available"):
            raise DropItem(f"Drop not available item: {item}")
        image_external_url = item.get("item_image")
        image_external_url = furl(image_external_url)
        if not all((image_external_url.scheme, image_external_url.netloc)):
            raise DropItem(
                f"Drop item with invalid item_image: {image_external_url.url}, " f"source_url: {item.get('source_url')}"
            )
        item_price = item.get("item_price")
        try:
            item_price = int(item_price)
        except (ValueError, TypeError) as e:
            logger.info(f"Invalid item_price: {item_price} for item: {item}")
            raise DropItem(f"Drop item with invalid price: {item_price}") from e
        try:
            self.cur.execute(
                f"""
            INSERT INTO {self.table_name} (store_id, version, name, price, image_external_url, source_url)
            VALUES ('{self.store_id}', '{self.version}', '{item.get('item_name')}', '{item_price}', '{image_external_url.url}', '{item.get('source_url')}');
            """
            )
            self.conn.commit()
        except psycopg2.Error as e:
            logger.error("Error:", e)
            self.conn.rollback()
        return item
