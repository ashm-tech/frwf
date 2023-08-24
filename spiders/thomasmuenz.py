import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreThomasmuenzSpider(scrapy.Spider):
    name = "thomasmuenz"
    base_url = furl("https://thomas-muenz.ru/")
    start_urls = ["https://thomas-muenz.ru/catalog/women/shoes/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css("a.pager__link::text")[-6].get())
        for page_number in range(1, max_page_number + 1):
            yield Request(response.url + f"?nav=page-{page_number}", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".product-card__title a.link").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".product-article__title::text").get()
        item_price = int(response.css('meta[itemprop="price"]').xpath("@content").get())

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
