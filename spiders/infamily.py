import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreInfamilySpider(scrapy.Spider):
    name = "infamily"
    base_url = furl("https://ln-family.com/")
    start_urls = ["https://ln-family.com/shop/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(30)
        for page_number in range(1, max_page_number + 1):
            yield Request(response.url + f"?page=page-{page_number}", self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".catalog-card__name a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = (
            response.css("picture source").xpath("@srcset").get().replace("120_3000_1", "625_3000_1")
        )
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".detail-main__title::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".price-item::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url.replace("%3Flocal=true", ""),
            "source_url": response.url,
        }
