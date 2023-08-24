import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreSelaSpider(scrapy.Spider):
    name = "sela"
    base_url = furl("https://www.sela.ru/")
    start_urls = [
        "https://www.sela.ru/eshop/women/",
        "https://www.sela.ru/eshop/kids/",
        "https://www.sela.ru/eshop/baby/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".pagination-wrapper__pagination-list-item::text")[-1].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".product-card a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        if "Нет" in response.css(".product-page__price-new::text").get():
            yield {"is_available": False}
        else:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".product-page__price-new::text").get()))
            item_image = response.css(".js-zoom-image").xpath("@src").get()
            item_name = response.css(".product-page__title::text").get()
            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
