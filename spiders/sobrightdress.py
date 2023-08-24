import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreSobrightdressSpider(scrapy.Spider):
    name = "sobrightdress"
    start_urls = ["https://sobrightdress.com/sitemap-store.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        items.remove("https://sobrightdress.com/catalog/tproduct/1-295804020251-dostavka-do-punkta-vidachi")
        items.remove("https://sobrightdress.com/catalog/tproduct/1-163249288331-doplata")
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css('meta[itemprop="image"]').xpath("@content").get()
        item_name = response.css('meta[property="og:title"]').xpath("@content").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css('meta[itemprop="price"]').xpath("@content").get())) // 100

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
