import re
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreEmkashopSpider(scrapy.Spider):
    name = "emkashop"
    start_urls = ["https://emkashop.ru/catalog"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(
                re.findall(r"\d{2}", response.css('div.pager li a::attr("href")').getall()[-1].split("&")[-1])[0]
            )
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css("div.lazy").css(".img-elem a").xpath("@href").getall():
            yield Request(item_url_path, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".product-col-right a").xpath("@href").get()
        item_name = response.css(".inner").css("h1::text").get().strip()
        item_price = int(response.css('[itemprop="price"]').xpath("@content").get())

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
