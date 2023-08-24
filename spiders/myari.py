import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreMyariSpider(scrapy.Spider):
    name = "myari"
    start_urls = ["https://myari.ru/shop/all"]

    def parse(self, response, **kwargs):
        for item in response.css(".product").xpath("@href").getall():
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = "https:" + response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".description .name::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product-price-min::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
