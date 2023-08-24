import re
import json
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreTottiShopSpider(scrapy.Spider):
    name = "tottishop"
    start_urls = ["https://totti-shop.ru/server-sitemap.xml"]

    def parse(self, response, **kwargs):
        soup = bs(response.text, "xml")
        table = [i.text for i in soup.findAll("loc")]
        items = sum(list(filter(None, [re.findall(r"https://totti-shop.ru/product-card/.*", i) for i in table])), [])
        for item in items:
            yield Request(item, self._parse_item_page)

    def _parse_item_page(self, response):
        json_rez = json.loads(response.css("script#__NEXT_DATA__::text").get())
        if response.status == 404:
            yield {"is_available": False}
        elif json_rez["props"]["pageProps"]["data"]["product"]["images"][0] == "/static/img/mock.jpg":
            yield {"is_available": False}
        else:
            item_name = response.css("h1::text").get()
            item_image = json_rez["props"]["pageProps"]["data"]["product"]["images"][0]
            item_price = int(re.sub(r"[^0-9]", "", response.css("div.Card_priceBlock__KqZym h1::text").get()))

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": response.url,
            }
