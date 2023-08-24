import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreAkhmadullinadreamsSpider(scrapy.Spider):
    name = "akhmadullinadreams"
    base_url = furl("https://akhmadullinadreams.com/")
    start_urls = [
        "https://akhmadullinadreams.com/catalog/odezhda/",
        "https://akhmadullinadreams.com/catalog/aksessuary/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".pages__numb ::text")[-1].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".product").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".myslider__item__image").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".pop-info__title h1::text").get()
        if response.css(".pop-info__price::text").get().strip() == "":
            item_price = int(re.sub(r"[^0-9]", "", response.css(".pop-info__price p::text").get()))
        else:
            item_price = int(re.sub(r"[^0-9]", "", response.css(".pop-info__price::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
