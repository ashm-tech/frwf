import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreBnprtSpider(scrapy.Spider):
    name = "bnprt"
    start_urls = ["https://bnprt.ru/product-sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        pattern = r"https://bnprt.ru/wp-content/.*"

        for item in items:
            if not re.match(pattern, item):
                yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css('meta[name="twitter:data1"]').xpath("@content").get() is not None:
            item_image = response.css('meta[property="og:image"]').xpath("@content").get()
            item_name = response.css('meta[property="og:image:alt"]').xpath("@content").get()
            item_price = int(re.sub(r"[^0-9]", "", response.css('meta[name="twitter:data1"]').xpath("@content").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
