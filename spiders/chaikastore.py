import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreChaikastoreSpider(scrapy.Spider):
    name = "chaikastore"
    base_url = furl("https://chaikastore.ru/")
    start_urls = [
        "https://chaikastore.ru/shop/odezhda/",
        "https://chaikastore.ru/shop/aksessuary",
        "https://chaikastore.ru/shop/kupalniki",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            if response.css(".nav-paginator__link::text").get() is None:
                max_page_number = 1
            else:
                max_page_number = int(response.css(".nav-paginator__link::text")[-3].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url in response.css(".static-grid-cell a").xpath("@href").getall():
            yield Request(item_url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = "https:" + response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".name::text").get()
        item_price = (
            int(re.sub(r"[^0-9]", "", response.css(".f__s_price-discount::text").get()))
            if response.css(".f__s_price-discount::text").get() is not None
            else int(re.sub(r"[^0-9]", "", response.css(".product-price-min::text").get()))
        )

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
