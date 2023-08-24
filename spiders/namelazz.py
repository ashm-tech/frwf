import copy
import json
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreNamelazzSpider(scrapy.Spider):
    name = "namelazz"
    base_url = furl("https://namelazz.com/")
    start_urls = ["https://namelazz.com/api/catalog/products/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(json.loads("".join(response.css(".prettyprint ::text").getall()[16::]))["num_pages"])
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_item_page)

    def _parse_item_page(self, response):
        items = json.loads("".join(response.css(".prettyprint ::text").getall()[16::]))["results"]
        for item in items:
            item_image = item["images"][0]["image_800x1000"]
            item_name = item["name"]
            item_price = int(item["price"])
            source_url = copy.deepcopy(self.base_url)
            source_url.add(item["detail_url"])

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": source_url.url.replace("?", "").replace("%2F", "/"),
            }
