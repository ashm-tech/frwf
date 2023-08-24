import copy
import logging

import scrapy
from furl import furl

logger = logging.getLogger(__name__)


class StoreSvyatayaSpider(scrapy.Spider):
    name = "svyataya"
    base_url = furl("https://svyataya.com/")
    start_urls = [
        "https://svyataya.com/catalog/women-s/",
        "https://svyataya.com/catalog/men-s/",
    ]

    def parse(self, response, **kwargs):
        for item in response.css(".catalog__card"):
            item_image_relative_path = item.css(".lazy-slider").xpath("@data-src").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = item.css(".card__discription::text").get()
            item_price = int(item.css(".card__price").xpath("@data-val").get())
            source_url = copy.deepcopy(self.base_url)
            source_url.add(item.css(".card__discription").xpath("@href").get())

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url.replace("?%2F", "").replace("%2F", "/"),
            }
