import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreFormsSpider(scrapy.Spider):
    name = "fourforms"
    base_url = furl("https://4forms.ru/")
    start_urls = ["https://4forms.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        table = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://4forms.ru/product/.*", i) for i in table])), [])
        for item in items:
            yield Request(item, self._product_id_parser)

    def _product_id_parser(self, response):
        product_id = int(response.css('div.product-info form::attr("data-product-id")').get())
        yield Request(f"https://4forms.ru/products_by_id/{product_id}.json", self._parse_item_page)

    def _parse_item_page(self, response):
        rez = response.json()["products"][0]
        item_name = rez["title"]
        if int(round(float(rez["price_min"]))) == int(round(float(rez["price_max"]))):
            item_price = int(round(float(rez["price_min"])))
        else:
            item_price = int(round(float(rez["price_man"])))
        item_image = rez["images"][0]["original_url"]
        url_relative_path = rez["url"]
        source_url = copy.deepcopy(self.base_url)
        source_url.add(url_relative_path)
        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
