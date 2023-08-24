import re
import copy
import json
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreToptopSpider(scrapy.Spider):
    name = "toptop"
    base_url = furl("https://toptop.ru/")
    start_urls = [
        "https://toptop.ru/catalog/clothes",
        "https://toptop.ru/catalog/shoes",
        "https://toptop.ru/catalog/accessories",
        "https://toptop.ru/catalog/beauty/skincare",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = (
                int(
                    re.sub(
                        r"[^0-9]", "", response.css(".Pagination-module__paginationCounter___2R5-y::text").getall()[-1]
                    )
                )
                // 48
            )

        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".catalog-item_link").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        rez = json.loads(response.css("body script::text").get())
        item_image = rez["image"]
        item_name = rez["name"]
        item_price = int(round(float(rez["offers"][0]["price"])))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
