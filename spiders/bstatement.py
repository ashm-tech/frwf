import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreBstatementSpider(scrapy.Spider):
    name = "bstatement"
    base_url = furl("https://bstatement.ru/")
    start_urls = ["https://bstatement.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        row_items = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://bstatement.ru/products/.*", i) for i in row_items])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css(".price__sale").get() is None:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".price::text").get()))
        else:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".price__sale::text").get()))

        if response.css('.background div::attr("style")').get() is None:
            yield dict(is_available=False)
        else:
            item_image_relative_path = re.findall(
                r"url\('(.+)'\)", response.css('.background div::attr("style")').get()
            )[0]
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)

            item_name = response.css(".name::text").get()

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": response.url,
            }
