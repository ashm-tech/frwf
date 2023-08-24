import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreZarinaSpider(scrapy.Spider):
    name = "zarina"
    base_url = furl("https://zarina.ru/")
    start_urls = ["https://zarina.ru/catalog/clothes/", "https://zarina.ru/man/clothes/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".pagination__list-item ::text").getall()[-2].strip())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".catalog__product-title").css("a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".product__media-item").css("img").xpath("@src").get()
        item_name = response.css(".product__title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product__price-current::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
