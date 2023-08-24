import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreCountrytextileSpider(scrapy.Spider):
    name = "countrytextile"
    base_url = furl("https://countrytextile.co/")
    start_urls = [
        "https://countrytextile.co/catalog/man/",
        "https://countrytextile.co/catalog/woman/",
    ]

    def parse(self, response, **kwargs):
        for item_url_path in response.css(".product").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".detail-img").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".detail-info h1::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".detail-price::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
