import re
import copy
import logging

import scrapy
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
from furl import furl
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StoreMonochromeSpider(scrapy.Spider):
    name = "monochrome"
    base_url = furl("https://monochrome.ru/")
    start_urls = ["https://monochrome.ru/shop/all"]

    custom_settings = {"CONCURRENT_REQUESTS": 1}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = uc.Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.implicitly_wait(30)
        soup = bs(self.driver.page_source, "lxml")
        items = soup.findAll("div", class_="shop_item")

        for item in items:
            item_image_relative_path = item.find("div", class_="shop_item__image").find("source").get("srcset")
            if item_image_relative_path is None:
                yield dict(is_available=False)
            else:
                item_image = copy.deepcopy(self.base_url)
                item_image.path.add(item_image_relative_path)
                item_name = item.find("div", class_="shop_item__name").text.strip()
                item_price = int(re.sub(r"[^0-9]", "", item.find("div", class_="shop_item__price").text))
                item_link_relative_path = item.find("a", class_="shop_item__link").get("href")
                source_url = copy.deepcopy(self.base_url)
                source_url.path.add(item_link_relative_path)

                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image.url,
                    "source_url": source_url.url,
                }
        self.driver.quit()
