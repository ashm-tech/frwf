import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreWonderwandershopSpider(scrapy.Spider):
    name = "wonderwandershop"
    start_urls = [
        "https://wonderwander-shop.com/ru/odezhda/posmotret-vse/",
        "https://wonderwander-shop.com/ru/accessories/posmotret-vse/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            if response.css(".ty-pagination__item::text").get() is None:
                max_page_number = 1
            else:
                max_page_number = int(response.css(".ty-pagination__item::text")[-2].get())
        for page_number in range(1, max_page_number + 1):
            yield Request(response.url + f"page-{page_number}", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url in response.css("b a").xpath("@href").getall():
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".cm-image").xpath("@src").get()
        item_name = response.css(".ty-product-block-title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".ty-price-num::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
