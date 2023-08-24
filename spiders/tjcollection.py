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


class StoreTjcollectionSpider(scrapy.Spider):
    name = "tjcollection"
    base_url = furl("https://tjcollection.ru/")
    start_urls = ["https://tjcollection.ru/catalog/woman/obuv/?page=178"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.implicitly_wait(60)
        iframe = self.driver.find_element(By.TAG_NAME, "footer")
        ActionChains(self.driver).scroll_to_element(iframe).perform()
        time.sleep(5)
        soup = bs(self.driver.page_source, "lxml")
        item_links = [i.get("href") for i in soup.findAll("a", class_="catalog_card__link")]
        self.driver.quit()
        for item_url_path in item_links:
            item_full_url_path = copy.deepcopy(self.base_url)
            item_full_url_path.path.add(item_url_path)
            yield Request(item_full_url_path.url, self._parse_item_page)

    def _parse_item_page(self, response):
        item_image_relative_path = response.css(".media_img").css("img").xpath("@src").get()
        item_image = copy.deepcopy(self.base_url)
        item_image.path.add(item_image_relative_path)
        item_name = response.css(".item_title::text").get()
        item_price = int(response.css('meta[property="product:price:amount"]').xpath("@content").get())

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image.url,
            "source_url": response.url,
        }
