import re
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreYanabesfamilnayaSpider(scrapy.Spider):
    name = "yanabesfamilnaya"
    base_url = furl("https://yanabesfamilnaya.com/")
    start_urls = ["https://yanabesfamilnaya.com/online-shop"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(re.sub(r"[^0-9]", "", response.css(".results::text").get().split("(")[1]))
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(
                url=page_url.url,
                callback=self._parse_catalog_page,
                cookies=dict(language="ru", currency="RUB", PHPSESSID="3b8e08f8a7035d3907475fb289ce6dd4"),
            )

    def _parse_catalog_page(self, response, **kwargs):
        for item_url in response.css(".has-second-image").xpath("@href").getall():
            yield Request(
                url=item_url,
                callback=self._parse_item_page,
                cookies=dict(language="ru", currency="RUB", PHPSESSID="3b8e08f8a7035d3907475fb289ce6dd4"),
                headers={"accept": "*/*", "accept-language": "ru,en;q=0.9", "user-agent": "parser ashm.tech"},
            )

    def _parse_item_page(self, response):
        item_image = response.css('img[itemprop="image"]').xpath("@src").get()
        item_name = response.css(".heading-title").css("::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product-price").css("::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
