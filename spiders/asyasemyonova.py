import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreAsyasemyonovaSpider(scrapy.Spider):
    name = "asyasemyonova"
    base_url = furl("https://asyasemyonova.ru/")
    start_urls = ["https://asyasemyonova.ru/magazin/folder/posmotret-vse"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".page-last ::text").get())
        for page_number in range(max_page_number):
            yield Request(response.url + f"/p/{page_number}", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".product-name a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".product_name::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".custom-buy-btn::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
