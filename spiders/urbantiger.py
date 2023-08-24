import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreUrbantigerSpider(scrapy.Spider):
    name = "urbantiger"
    base_url = furl("https://urbantiger.ru/")
    start_urls = [
        "https://urbantiger.ru/katalog/woman/smotret-vse/",
        "https://urbantiger.ru/katalog/men/smotret-vse/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".nav-link::text")[-3].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_2": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item in response.css(".card"):
            item_image_relative_path = re.findall(r"url\('(.+)'\)", item.css(".card-img::attr(style)").get())[0]
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = item.css(".link-gray-lighter::text").get()
            if item.css(".c-orange::text").get() is not None:
                item_price = item.css(".c-orange::text").get()
            else:
                item_price = int(re.sub(r"[^0-9]", "", item.css(".card__price ::text").get()))
            source_url = copy.deepcopy(self.base_url)
            source_url.path.add(item.css(".card-name__link").xpath("@href").get())

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url,
            }
