import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreMollisSpider(scrapy.Spider):
    name = "mollis"
    start_urls = ["https://new.mollis.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://new.mollis.ru/product/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_id)

    def _parse_item_id(self, response):
        item_id = response.css("form").xpath("@data-product-id").get()

        yield Request(f"https://new.mollis.ru/products_by_id/{item_id}.json", self._parse_item_page, method="POST")

    def _parse_item_page(self, response):
        rez = response.json()
        if not rez["products"][0]["available"]:
            yield {"is_available": False}
        else:
            if rez["products"][0]["images"] == []:
                item_image = None
            else:
                item_image = rez["products"][0]["images"][0]["original_url"]
            item_name = rez["products"][0]["title"]
            item_price = int(round(float(rez["products"][0]["variants"][0]["base_price"])))
            source_url = "https://new.mollis.ru" + rez["products"][0]["url"]

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": source_url,
            }
