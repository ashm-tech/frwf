import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreSpider(scrapy.Spider):
    name = "moodstore"
    base_url = furl("https://www.2moodstore.com/")
    start_urls = ["https://www.2moodstore.com/collection/all/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = max(
                int(number)
                for number in response.css(".pagination-custom").css("a").css("::text").getall()
                if number.isdigit()
            )
        logger.info(f"Scrape max_page_number: {max_page_number}")

        for page_number in range(1, max_page_number + 1):
            page_url = copy.deepcopy(self.base_url)
            page_url.path.add("collection/all/")
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".product-related-color-item").css("a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        is_available = bool(response.css(".product-available").get())
        if not is_available:
            yield {
                "is_available": is_available,
            }
        else:
            item_name = response.css(".product-title").css("::text").get()
            item_price = int(re.sub(r"[^0-9]", "", response.css(".product-price").css("::text").get()))
            item_image = response.css(".ProductImg-product").xpath("@src").get()
            item_image_url = furl(item_image)
            # sometimes images urls has no host. skip it.
            if item_image_url.host is None:
                yield {
                    "is_available": False,
                }
            else:
                yield {
                    "is_available": is_available,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image,
                    "source_url": response.url,
                }
