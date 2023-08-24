import re
import copy
import time
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from scrapy.http import Request
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StoreShitrendySpider(scrapy.Spider):
    name = "shitrendy"
    base_url = furl("https://shitrendy.com/")
    start_urls = ["https://shitrendy.com/catalog"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.implicitly_wait(60)
        iframe = self.driver.find_element(By.CLASS_NAME, "fadeInUp")
        for i in range(25):
            ActionChains(self.driver).scroll_to_element(iframe).perform()
            time.sleep(0.1)
        soup = bs(self.driver.page_source, "lxml")
        item_links = [i.find("a").get("href") for i in soup.findAll("div", class_="product-card")]
        self.driver.quit()
        for item_url_path in item_links:
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image = response.css("img.abs").xpath("@src").get()
        item_name = response.css(".title ::text").get()
        item_price = int(re.sub(r"[^0-9]", "", response.css(".price ::text").get()))

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
