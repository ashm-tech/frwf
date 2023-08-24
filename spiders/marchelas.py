import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreMarchelasSpider(scrapy.Spider):
    name = "marchelas"
    start_urls = ["https://marchelas.com/category/clothing/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".page-numbers::text")[-4].get())
        for page_number in range(1, max_page_number + 1):
            yield Request(f"https://marchelas.com/category/clothing/page/{page_number}/", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url in response.css(".product a").xpath("@href").getall():
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".zoom-link").xpath("@href").get()
        item_name = response.css(".title ::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".woocommerce-Price-amount ::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
