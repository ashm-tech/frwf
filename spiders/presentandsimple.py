import logging

import scrapy

logger = logging.getLogger(__name__)


class StorePresentandsimpleSpider(scrapy.Spider):
    name = "presentandsimple"
    start_urls = ["https://presentandsimple.com/api/categories/"]

    def parse(self, response, **kwargs):
        rez = response.json()["data"]
        for category in rez:
            for product in category["data"]["attributes"]["products"]["data"]:
                item_name = product["data"]["attributes"]["title_for_site"]
                item_price = int(product["data"]["attributes"]["cost"])
                item_image = product["data"]["attributes"]["images"]["data"][0]["data"]["attributes"]["path"]
                source_url = product["links"]["self"]

                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image,
                    "source_url": source_url,
                }
