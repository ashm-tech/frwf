import re
import copy
import time
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from furl import furl
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StorePostpostscriptumSpider(scrapy.Spider):
    name = "postpostscriptum"
    base_url = furl("https://post-post-scriptum.com/")
    start_urls = ["https://post-post-scriptum.com/catalog/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.implicitly_wait(60)
        iframe = self.driver.find_element(By.CLASS_NAME, "mugen-scroll")

        for i in range(40):
            ActionChains(self.driver).scroll_to_element(iframe).perform()
            self.driver.execute_script("window.scrollBy(0,100)", "")

            time.sleep(1)

        soup = bs(self.driver.page_source, "lxml")

        self.driver.quit()

        items = soup.findAll("div", class_="col--no-padding")

        for item in items:
            item_image = item.find("div", class_="product__link").find("img").get("data-src")
            item_name = item.find("div", class_="product__title").text.strip()
            item_price = int(re.sub(r"[^0-9]", "", item.find("div", class_="product__discount-price").text))
            item_raw_link = item.find("a", class_="product").get("href")
            source_url = copy.deepcopy(self.base_url)
            source_url.path.add(item_raw_link)

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": source_url.url,
            }
