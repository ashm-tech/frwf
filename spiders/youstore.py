import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreYoustoreSpider(scrapy.Spider):
    name = "youstore"
    start_urls = ["https://youstore.one/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://youstore.one/catalog/.*/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css("#product-view").get() is not None:
            item_image = response.css('meta[property="og:image"]').xpath("@content").get()
            item_name = response.css(".column-info h1::text").get()
            if response.css(".discount::text").get() is not None:
                item_price = int(re.sub(r"[^0-9]", "", response.css(".discount::text").get()))
            else:
                item_price = int(re.sub(r"[^0-9]", "", response.css(".product-view-price price::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
