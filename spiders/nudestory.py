import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreNudestorySpider(scrapy.Spider):
    name = "nudestory"
    base_url = furl("https://nudestory.ru/")
    start_urls = ["https://nudestory.ru/catalog/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(34)
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_3": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".catalog__item").css("a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        try:
            item_image_relative_path = response.css(".catalog-page__images-a").css("img").xpath("@src").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
        except:
            item_image = None
        item_name = response.css(".catalog-page__title::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".catalog-page__fullprice::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
