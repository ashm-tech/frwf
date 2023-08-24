import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreDarsiStudioSpider(scrapy.Spider):
    name = "darsistudio"
    base_url = furl("https://darsi.studio/")
    start_urls = ["https://darsi.studio/collection/woman"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".pagination-node::text")[-3].get().strip())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".hide-sm").css("a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url + ".json", self._parse_item_page)

    def _parse_item_page(self, response):
        rez = response.json()["product"]
        item_image = rez["images"][0]["original_url"]
        item_name = rez["title"]
        item_price = (
            int(round(float(rez["price_min"])))
            if rez["price_min"] == rez["price_max"]
            else int(round(float(rez["price_max"])))
        )
        source_url = copy.deepcopy(self.base_url)
        source_url.add(rez["url"])

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": source_url.url.replace("%2F", "/").replace("?", ""),
        }
