import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreEkonikaSpider(scrapy.Spider):
    name = "ekonika"
    base_url = furl("https://ekonika.ru/")
    start_urls = ["https://ekonika.ru/sitemap_item_4.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        for item in items:
            yield Request(
                url=item,
                callback=self._parse_item_page,
                method="POST",
                headers={"accept": "*/*", "user-agent": "parser"},
            )

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css('h1[itemprop="name"]::text').get()
        item_price = int(re.sub(r"[^0-9]", "", response.css('meta[itemprop="price"]').xpath("@content").get())) // 100

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
