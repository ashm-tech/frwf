import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreLiklabSpider(scrapy.Spider):
    name = "liklab"
    base_url = furl("https://liklab.com/")
    start_urls = ["https://liklab.com/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://liklab.com/catalog/.*/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css(".ll-product").get() is not None:
            if response.css(".ll-product__img").xpath("@src").get() is None:
                item_image = None
            else:
                item_image_relative_path = response.css(".ll-product__img").xpath("@src").get()
                item_image = copy.deepcopy(self.base_url)
                item_image.path.add(item_image_relative_path)
            item_name = response.css(".ll-h1::text").get()
            item_price = int(re.sub(r"[^0-9]", "", response.css(".ll-product__price::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": response.url,
            }
