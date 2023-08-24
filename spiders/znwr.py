import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreZnwrSpider(scrapy.Spider):
    name = "znwr"
    base_url = furl("https://znwr.ru/")
    start_urls = ["https://znwr.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://znwr.ru/product/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".swiper-lazy").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".product__title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product__price-new::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
