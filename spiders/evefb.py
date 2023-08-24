import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreEvefbSpider(scrapy.Spider):
    name = "evefb"
    start_urls = ["https://evefb.ru/sitemap-iblock-16.xml", "https://evefb.ru/sitemap-iblock-17.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        for item in items:
            yield Request(item, self._parse_item)

    def _parse_item(self, response):
        if response.css('meta[itemprop="price"]').xpath("@content").get() is not None:
            item_image = response.css('meta[name="og:image"]').xpath("@content").get()
            item_name = response.css('meta[itemprop="name"]').xpath("@content").get()
            item_price = int(response.css('meta[itemprop="price"]').xpath("@content").get().strip())

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
