import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreAmestoreSpider(scrapy.Spider):
    name = "amestore"
    base_url = furl("https://ame-store.ru/")
    start_urls = ["https://ame-store.ru/ajax/catalog.php"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            """
            Infinite pagination with repeated data.
            Up to page 35, all data is not repeated
            """
            max_page_number = int(35)
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in sum(
            list(
                filter(
                    None,
                    [
                        re.findall(r"/catalog/.*", i)
                        for i in response.css(".show-me-fast-look a").xpath("@href").getall()
                    ],
                )
            ),
            [],
        ):
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".detail-pic-class").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".catalog-item-name::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".price-detail::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
