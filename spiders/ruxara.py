import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreRuxaraSpider(scrapy.Spider):
    name = "ruxara"
    base_url = furl("https://ruxara.ru/")
    start_urls = [
        "https://ruxara.ru/kupalniki_plyazhnye_tuniki/",
        "https://ruxara.ru/aksessuary/",
        "https://ruxara.ru/verkhnyaya_odezhda/",
        "https://ruxara.ru/platya/",
        "https://ruxara.ru/zhakety/",
        "https://ruxara.ru/bluzy_i_rubashki/",
        "https://ruxara.ru/bryuki/",
        "https://ruxara.ru/yubki/",
        "https://ruxara.ru/vodolazki/",
        "https://ruxara.ru/dzhempery/",
        "https://ruxara.ru/zhilety/",
        "https://ruxara.ru/kardigany/",
        "https://ruxara.ru/kombinezony/",
        "https://ruxara.ru/futbolki/",
        "https://ruxara.ru/kofty/",
        "https://ruxara.ru/svitery/",
        "https://ruxara.ru/svitshoty/",
        "https://ruxara.ru/topy/",
        "https://ruxara.ru/tolstovki/",
        "https://ruxara.ru/tuniki/",
        "https://ruxara.ru/kostyumy/",
        "https://ruxara.ru/shorty/",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = (
                int(1)
                if response.css(".pagination") == []
                else int(response.css(".pagination").css("a::text")[-2].get())
            )
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".bx_catalog_item_title a").xpath("@href").getall():
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url.replace("%3F", "?"), self._parse_item_page)

    def _parse_item_page(self, response):
        if response.css(".item_current_price::text").get() is None:
            yield {"is_available": False}
        else:
            item_image_relative_path = response.css(".imageFullScreens").xpath("@href").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = response.css(".bx_item_title h1 ::text").get().strip()
            item_price = int(re.sub(r"[^0-9]", "", response.css(".item_current_price::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": response.url,
            }
