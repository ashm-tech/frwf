import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreRogovshopSpider(scrapy.Spider):
    name = "rogovshop"
    start_urls = ["https://rogovshop.ru/index.php?route=extension/feed/google_sitemap"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://rogovshop.ru/.*product_id=.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".product-card__image img").xpath("@src").get()
        item_name = response.css(".product-card__title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product-card__price span::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
