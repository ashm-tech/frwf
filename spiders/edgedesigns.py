import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreEdgedesignsSpider(scrapy.Spider):
    name = "edgedesigns"
    start_urls = ["https://edgedesigns.ru/sitemap-shop.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://edgedesigns.ru/product/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css('meta[property="og:title"]').xpath("@content").get()
        item_price = int(response.css('meta[property="product:price:amount"]').xpath("@content").get())

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
