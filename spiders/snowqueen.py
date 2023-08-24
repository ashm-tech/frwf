import re
import copy
import logging

import scrapy
import undetected_chromedriver as uc
from furl import furl
from parsel import Selector
from scrapy.http import Request
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StoreSnowqueenSpider(scrapy.Spider):
    name = "snowqueen"
    base_url = furl("https://snowqueen.ru/")
    start_urls = [
        *[f"https://snowqueen.ru/catalog/muzhskaya-odezhda?p={i}" for i in range(1, 79)],
        *[f"https://snowqueen.ru/catalog/zhenskaya-odezhda?p={i}" for i in range(1, 264)],
    ]

    custom_settings = {"CONCURRENT_REQUESTS": 1}

    def __init__(self, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = uc.Chrome(options=chrome_options)
        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, meta=dict(dont_redirect=True), callback=self.parse)

    def parse(self, response, **kwargs):
        try:
            self.driver.get(response.url)
            html = Selector(text=self.driver.page_source)
            items = html.css(".product")
            for item in items:
                item_image_relative_path = item.css('meta[itemprop="image"]').xpath("@content").get()
                item_image = copy.deepcopy(self.base_url)
                item_image.path.add(item_image_relative_path)
                item_name = item.css(".product__name::text").get().strip()
                item_price = int(re.sub(r"[^0-9]", "", item.css('span[property="price"]::text').get()))
                item_url = item.css(".product-link").xpath("@href").get()
                source_url = copy.deepcopy(self.base_url)
                source_url.path.add(item_url)
                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image.url,
                    "source_url": source_url.url,
                }
        except:
            yield dict(is_available=False)
