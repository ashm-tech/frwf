import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreWearmellowSpider(scrapy.Spider):
    name = "wearmellow"
    start_urls = ["https://wearmellow.store/shop/"]

    def parse(self, response, **kwargs):
        for item_url in response.css(".static-grid-item").css(".product").xpath("@href").getall():
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = "http:" + response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".description h1::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product-price-min::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
