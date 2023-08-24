import re
import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreBarmariskaSpider(scrapy.Spider):
    name = "barmariska"
    start_urls = ["https://barmariska.ru/shop/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".page-numbers::text")[-3].get())
        for page_number in range(1, max_page_number + 1):
            yield Request(f"https://barmariska.ru/shop/page/{page_number}/", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url in sum(
            list(
                filter(
                    None,
                    [
                        re.findall(r"https://barmariska.ru/shop/.*", i)
                        for i in response.css(".type-product a").xpath("@href").getall()
                    ],
                )
            ),
            [],
        ):
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".product_title::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".woocommerce-Price-amount bdi::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
