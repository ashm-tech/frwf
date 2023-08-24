import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreShuclothesSpider(scrapy.Spider):
    name = "shuclothes"
    start_urls = [
        "https://shuclothes.com/ru/man",
        "https://shuclothes.com/ru/woman",
    ]

    def parse(self, response, **kwargs):
        items = response.css(".relative a").xpath("@href").getall()
        items.remove("/")
        for item_url in items:
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css(".mb-60").get() is not None:
            item_image = response.css('meta[property="og:image"]').xpath("@content").get()
            item_name = response.css('meta[property="og:title"]').xpath("@content").get()
            item_price = int(re.sub(r"[^0-9]", "", response.css(".whitespace-nowrap::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
