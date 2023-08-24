import re
import copy
import logging

import scrapy
from furl import furl

logger = logging.getLogger(__name__)


class StoreIamstudioSpider(scrapy.Spider):
    name = "iamstudio"
    base_url = furl("https://iamstudio.ru/")
    start_urls = [
        "https://iamstudio.ru/catalog/",
    ]

    def parse(self, response, **kwargs):
        items = response.css(".item1")
        for item in items:
            price = item.css("._real::text").get().replace("\n", "").strip()
            if not price:
                yield {"is_available": False}
            else:
                item_price = int(re.sub(r"[^0-9]", "", price))
                name = item.css("._title::text").get()
                image_relative_path = item.css("img").xpath("@src").get()
                image_url = copy.deepcopy(self.base_url)
                image_url.path.add(image_relative_path)
                source_url_relative_path = item.css(".item_detail_link").xpath("@href").get()
                source_url = copy.deepcopy(self.base_url)
                source_url.path.add(source_url_relative_path)
                yield {
                    "is_available": True,
                    "item_name": name,
                    "item_price": item_price,
                    "item_image": image_url.url,
                    "source_url": source_url.url,
                }
