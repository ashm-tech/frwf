import re
import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreTheselectSpider(scrapy.Spider):
    name = "theselect"
    base_url = furl("https://theselect.ru/")
    start_urls = ["https://theselect.ru/sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [
            *sum(
                list(
                    filter(
                        None,
                        [
                            re.findall(r"https://theselect.ru/en/collection/zhenshhinam/.*/.*", i)
                            for i in [i.text for i in soup.findAll("loc")]
                        ],
                    )
                ),
                [],
            ),
            *sum(
                list(
                    filter(
                        None,
                        [
                            re.findall(r"https://theselect.ru/en/collection/deti/.*/.*", i)
                            for i in [i.text for i in soup.findAll("loc")]
                        ],
                    )
                ),
                [],
            ),
        ]
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css(".flex-md-row").get() is not None:
            item_image_relative_path = response.css(".sel-product-main__img-box").css("source").xpath("@srcset").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = response.css(".sel-product-main__title::text").get()
            item_price = int(re.sub(r"[^0-9]", "", response.css(".sel-product-main__price::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": response.url,
            }
