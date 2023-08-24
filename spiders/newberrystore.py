import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreNewberrystoreSpider(scrapy.Spider):
    name = "newberrystore"
    start_urls = ["https://newberrystore.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://newberrystore.ru/product/.*", i) for i in row_items])), [])

        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".product__title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css('meta[name="description"]').xpath("@content").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
