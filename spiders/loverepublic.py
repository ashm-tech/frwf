import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreLoverepublicSpider(scrapy.Spider):
    name = "loverepublic"
    base_url = furl("https://loverepublic.ru")
    start_urls = ["https://loverepublic.ru/catalog/odezhda/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".router-link-active").css("span::text")[-1].get())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page, method="POST")

    def _parse_catalog_page(self, response, **kwargs):
        if response.status == 504:
            pass
        else:
            for item_id in [
                i.split("/")[-2] for i in response.css(".catalog-item__name").css("a").xpath("@href").getall()
            ]:
                yield Request(
                    f"https://api.loverepublic.ru/web/v1/catalog/products/{item_id}/stock", self._parse_item_page
                )

    def _parse_item_page(self, response):
        rez: dict = response.json()["data"]
        item_image = rez["images"]["original"][0]
        item_name = rez["detailName"]
        item_price = int(rez["sku"][0]["properties"]["starayaTsena"]["value"])
        source_url = copy.deepcopy(self.base_url)
        source_url.add(rez["link"])

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": source_url.url.replace("%2F", "/").replace("?", ""),
        }
