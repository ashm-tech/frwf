import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreImoceanSpider(scrapy.Spider):
    name = "imocean"
    base_url = furl("https://imocean.ru/")
    start_urls = [
        "https://imocean.ru/katalog/platya.html",
        "https://imocean.ru/katalog/topy-i-bluzy.html",
        "https://imocean.ru/katalog/rubashki.html",
        "https://imocean.ru/katalog/yubki-i-bryuki.html",
        "https://imocean.ru/katalog/bryuki.html",
        "https://imocean.ru/katalog/zhakety.html",
        "https://imocean.ru/katalog/kostyumy.html",
        "https://imocean.ru/katalog/kostyumy-1.html",
        "https://imocean.ru/katalog/verhnyaya-odezhda.html",
    ]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            try:
                max_page_number = int(response.css(".pagination__link::text")[-1].get())
            except:
                max_page_number = 1

        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"page": page_number})

            yield Request(page_url.url, self._parse_catalog_page)

    def _parse_catalog_page(self, response, **kwargs):
        for item_url_path in response.css(".unit__link").xpath("@href").getall():
            yield Request(item_url_path, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css(".goods-image__link").xpath("@href").get()
        item_name = response.css(".hidden-md::text").get()
        item_price = int(response.css(".goods__price_js").xpath("@price").get())

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
