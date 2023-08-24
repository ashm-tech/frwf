import json
import logging

import scrapy

logger = logging.getLogger(__name__)


class StoreBlcvSpider(scrapy.Spider):
    name = "blcv"
    start_urls = [
        "https://store.tildacdn.com/api/getproductslist/"
        + "?storepartuid=954132044381"
        + "&recid=60264408"
        + "&c=1688572218682"
        + "&getparts=true"
        + "&getoptions=true"
        + "&slice=1"
        + "&size=100"
    ]

    def parse(self, response, **kwargs):
        for item in response.json()["products"]:
            item_image = json.loads(item["gallery"])[0]["img"]
            item_name = item["title"]
            item_price = int(round(float(item["price"])))
            source_url = item["url"]

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": source_url,
            }
