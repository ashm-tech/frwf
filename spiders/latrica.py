import re
import copy
import logging

import scrapy
from furl import furl

logger = logging.getLogger(__name__)


class StoreLatrikaSpider(scrapy.Spider):
    name = "latrika"
    base_url = furl("https://www.latrika.com/")
    start_urls = [
        "https://www.latrika.com/collection/marsvenus",
        "https://www.latrika.com/collection/dzhinsy",
        "https://www.latrika.com/collection/platya",
        "https://www.latrika.com/collection/bryuki",
        "https://www.latrika.com/collection/rubashki",
        "https://www.latrika.com/collection/verhnyaya-odezhda",
        "https://www.latrika.com/collection/denim",
        "https://www.latrika.com/collection/basic",
        "https://www.latrika.com/collection/svitshoty",
    ]

    def parse(self, response, **kwargs):
        items = response.css(".product-preview")
        for item in items:
            item_buttons = item.css(".product-preview__controls").css("button").getall()
            if len(item_buttons) == 2:
                item_price = int(re.sub(r"[^0-9]", "", item.css(".product-preview__price-cur ::text").get()))
                item_name = item.css(".product-preview__title a ::text").get()
                item_image = item.css("img").xpath("@data-src").get()
                source_url_relative_path = item.css("a").xpath("@href").get()
                source_url = copy.deepcopy(self.base_url)
                source_url.path.add(source_url_relative_path)
                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image,
                    "source_url": source_url.url,
                }
            else:
                yield {
                    "is_available": False,
                }
