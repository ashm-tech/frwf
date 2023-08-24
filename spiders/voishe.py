import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreVoisheSpider(scrapy.Spider):
    name = "voishe"
    start_urls = ["https://www.voishe.ru/sitemap-store.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_name = response.css("h1.js-store-prod-name::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css("div.js-store-prod-price-val::text").get())) // 100
        item_image = re.findall(r"url\((.*?)\)", response.css("div.t-container div.js-product-img").get())[0]
        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
