import re
import copy
import time
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request
from selenium.webdriver import ActionChains
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StoreLigioSpider(scrapy.Spider):
    name = "ligio"
    base_url = furl("https://ligio.ru/")
    start_urls = ["https://ligio.ru/catalog/"]

    custom_settings = {"CONCURRENT_REQUESTS": 1}

    def __init__(self, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)
        super().__init__(**kwargs)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.implicitly_wait(60)
        iframe = self.driver.find_element(By.TAG_NAME, "footer")
        for i in range(25):
            ActionChains(self.driver).scroll_to_element(iframe).perform()
            time.sleep(0.1)
        soup = bs(self.driver.page_source, "lxml")
        item_links = [i.get("href") for i in soup.findAll("a", class_="catalog-item")]
        self.driver.quit()
        for item_url_path in item_links:
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".card-img-big").css("img").xpath("@zoom-src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".page-title h1::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".item-price::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
