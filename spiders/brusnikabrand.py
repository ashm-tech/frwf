import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreBrusnikabrandSpider(scrapy.Spider):
    name = "brusnikabrand"
    base_url = furl("https://brusnikabrand.com/")
    start_urls = [
        "https://brusnikabrand.com/catalog/sport/",
        "https://brusnikabrand.com/catalog/linen_collection/",
        "https://brusnikabrand.com/catalog/platya_kombinezony_1/",
        "https://brusnikabrand.com/catalog/dzhempery_1/",
        "https://brusnikabrand.com/catalog/topy_1/",
        "https://brusnikabrand.com/catalog/bodi/",
        "https://brusnikabrand.com/catalog/rubashki_1/",
        "https://brusnikabrand.com/catalog/bryuki_1/",
        "https://brusnikabrand.com/catalog/dzhinsy/",
        "https://brusnikabrand.com/catalog/yubki/",
        "https://brusnikabrand.com/catalog/futbolki_/",
        "https://brusnikabrand.com/catalog/vodolazki_1/",
        "https://brusnikabrand.com/catalog/zhakety_/",
        "https://brusnikabrand.com/catalog/kardigany_/",
        "https://brusnikabrand.com/catalog/bombery/",
        "https://brusnikabrand.com/catalog/zhilety_/",
        "https://brusnikabrand.com/catalog/verkhnyaya_odezhda_1/",
        "https://brusnikabrand.com/catalog/komplekty_1/",
        "https://brusnikabrand.com/catalog/shorty/",
        "https://brusnikabrand.com/catalog/aksessuary_1/",
        "https://brusnikabrand.com/catalog/deti_1/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".pagination__one::text").getall()[-2])
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_5": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".catalog-item a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".swiper-wrapper").css("img").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".product-title::text").get().strip()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".product-price::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
