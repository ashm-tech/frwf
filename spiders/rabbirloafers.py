import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreRabbitloafersSpider(scrapy.Spider):
    name = "rabbitloafers"
    base_url = furl("https://rabbit-loafers.ru/")
    start_urls = ["https://rabbit-loafers.ru/ru/product/womans-loafers"]

    def parse(self, response, **kwargs):
        for item_url_path in response.css("ul.category__list2 li").css("a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".product__title::text").get()
        if response.css(".product__price-new::text").get() is None:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".product__price::text").get()))
        else:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".product__price-new::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
