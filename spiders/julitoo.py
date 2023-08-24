import re
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreJulitooSpider(scrapy.Spider):
    name = "julitoo"
    base_url = furl("https://julitoo.ru/")
    start_urls = ["https://julitoo.ru/shop/page/2/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(re.sub(r"[^0-9]", "", response.css("title::text").get().split("из")[-1]))
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.path.segments[-2] = page_number

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        table = response.css("h3.wd-entities-title").css("a").xpath("@href").getall()
        items = sum([[i] for i in table if not re.findall(r"https://julitoo.ru/shop/podarki/.*", i)], [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".woocommerce-product-gallery__image").css("a").xpath("@href").get()
        item_name = response.css(".entry-title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".price ::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
