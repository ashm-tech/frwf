import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreNevalenkiSpider(scrapy.Spider):
    name = "nevalenki"
    base_url = furl("https://nevalenki.com/")
    start_urls = ["https://nevalenki.com/catalog"]

    def parse(self, response, **kwargs):
        items = response.css(".good-item__title a").xpath("@href").getall()
        items.remove("")
        items.remove("")
        for item_url_path in items:
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css('meta[property="og:title"]').xpath("@content").get()
        item_price = int(
            re.sub(r"[^0-9]", "", response.css('meta[property="product:price:amount"]').xpath("@content").get())
        )

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
