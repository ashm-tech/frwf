import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreAllweneedSpider(scrapy.Spider):
    name = "allweneed"
    base_url = furl("https://allweneed.ru/")
    start_urls = ["https://allweneed.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        table = [i.text for i in soup.findAll("loc")]
        items = [
            "https://api.allweneed.ru/api/ru/catalog/products/" + i.split("/")[-1]
            for i in sum(list(filter(None, [re.findall(r"https://allweneed.ru/product/.*", i) for i in table])), [])
        ]
        for item in items:
            yield Request(item, self._parse_item_page, headers={"accept": "*/*", "user-agent": "PyCharm 2023"})

    def _parse_item_page(self, response):
        if response.json()["in_stock"]:
            name = response.json()["slug"]
            category = response.json()["category"]["slug"]
            item_image_relative_path = response.json()["image"]
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = response.json()["title"]
            item_price = int(round(float(response.json()["price"])))
            source_url = f"https://allweneed.ru/product/{category}/{name}"

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url,
            }
        else:
            yield {"is_available": False}
