import copy
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreRespectshoesSpider(scrapy.Spider):
    name = "respectshoes"
    base_url = furl("https://respect-shoes.ru/")
    start_urls = ["https://respect-shoes.ru/sitemap-iblock-16.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        items = [i.text for i in soup.findAll("loc")]
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css('h1[itemprop="name"]::text').get() is not None:
            if (
                response.css('meta[itemprop="price"]').xpath("@content").get() is None
                or response.css(".sp-thumbnail-image").xpath("@src").get() is None
            ):
                yield dict(is_available=False)

            else:
                image_row_path = response.css(".sp-thumbnail-image").xpath("@src").get().split("/")
                item_image_relative_path = f"/upload/iblock/{image_row_path[-3]}/{image_row_path[-1]}"
                item_image = copy.deepcopy(self.base_url)
                item_image.path.add(item_image_relative_path)
                item_name = response.css('h1[itemprop="name"]::text').get()
                item_price = int(response.css('meta[itemprop="price"]').xpath("@content").get())

                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image.url,
                    "source_url": response.url,
                }
