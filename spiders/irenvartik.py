import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreIrenvartikSpider(scrapy.Spider):
    name = "irenvartik"
    base_url = furl("https://irenvartik.ru/")
    start_urls = ["https://irenvartik.ru/obuv/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".page-navigation a::text")[-1].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item in response.css(".product-preview"):
            source_url = copy.deepcopy(self.base_url)
            source_url.path.add(item.css(".product-preview").xpath("@href").get())
            item_image_relative_path = item.css(".product-preview__img").xpath("@data-lazy").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = item.css(".product-preview__title::text").get()
            item_price = int(re.sub(r"[^0-9]", "", item.css(".product-preview__price::text").get().split("rub")[0]))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url,
            }
