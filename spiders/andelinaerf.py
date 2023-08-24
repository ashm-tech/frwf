import re
import copy
import logging

import scrapy
from furl import furl

logger = logging.getLogger(__name__)


class StoreAngelinaerfSpider(scrapy.Spider):
    name = "angelinaerf"
    base_url = furl("https://angelinaerf.ru/")
    start_urls = [
        "https://angelinaerf.ru/shop/dlya-nego/",
        "https://angelinaerf.ru/shop/novinki/",
        "https://angelinaerf.ru/shop/coats/",
        "https://angelinaerf.ru/shop/trenchi/",
        "https://angelinaerf.ru/shop/zhakety/",
        "https://angelinaerf.ru/shop/zhilety/",
        "https://angelinaerf.ru/shop/platya/",
        "https://angelinaerf.ru/shop/rubashki-i-bluzy/",
        "https://angelinaerf.ru/shop/Svitera-trikotage/",
        "https://angelinaerf.ru/shop/Telnyashki-longslivy/",
        "https://angelinaerf.ru/shop/kostyumy/",
        "https://angelinaerf.ru/shop/yubki/",
        "https://angelinaerf.ru/shop/shorty/",
        "https://angelinaerf.ru/shop/bryuki-dzhinsy-shorty/",
        "https://angelinaerf.ru/shop/futbolki%20i%20polo/",
        "https://angelinaerf.ru/shop/topy/",
        "https://angelinaerf.ru/shop/kombinezony/",
        "https://angelinaerf.ru/shop/Osobyy-sluchay/",
        "https://angelinaerf.ru/shop/aksessuary/",
    ]

    def parse(self, response, **kwargs):
        items = response.css(".card-item")
        for item in items:
            item_price = int(re.sub(r"[^0-9]", "", item.css(".price::text").get()))
            item_name = item.css(".card-body a::text").get()
            item_image_relative_path = item.css(".lazyload").xpath("@data-src").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            source_url_relative_path = item.css(".card-header a").xpath("@href").get()
            source_url = copy.deepcopy(self.base_url)
            source_url.path.add(source_url_relative_path)
            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url,
            }
