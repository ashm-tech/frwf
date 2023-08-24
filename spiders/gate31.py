import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreGate31Spider(scrapy.Spider):
    name = "gate31"
    base_url = furl("https://www.gate31.ru/")
    start_urls = [
        "https://www.gate31.ru/collection/vsya-kollektsiya",
        "https://www.gate31.ru/collection/men",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            numbers = response.css(".collection__pagination").css(".pagination__link").css("::text").getall()
            numbers = [n.replace("\n", "").strip() for n in numbers]
            max_page_number = max(int(number) for number in numbers if number.isdigit())
        logger.info(f"Scrape max_page_number: {max_page_number}")

        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})
            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        links = response.css(".product-card__link").xpath("@href").getall()
        for item_url_path in links:
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path.strip())
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_name = response.css(".product__title ::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product__price").css("::text").get()))
        item_image = response.css(".product__gallery-image").xpath("@src").get()
        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
