import re
import json
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreStoreezSpider(scrapy.Spider):
    name = "storeez"
    base_url = furl("https://12storeez.com/")

    def start_requests(self):
        start_urls = ["https://12storeez.com/catalog/womencollection", "https://12storeez.com/catalog/mencollection"]
        for url in start_urls:
            yield Request(url, self.parse, method="POST")

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(25)  # Endless Pagination
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page, method="POST")

    def _parse_catalog_page(self, response, **kwargs):
        for item_full_url_path in sum(
            list(
                filter(
                    None,
                    [
                        re.findall(r"https://12storeez.com/catalog/.*", i)
                        for i in response.css("div").css(".catalogPage").css("a").xpath("@href").getall()
                    ],
                )
            ),
            [],
        ):
            yield Request(item_full_url_path, self._parse_item_page, method="POST")

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css(".ProductSummary__title::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".ProductSummary__cost::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
