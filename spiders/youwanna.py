import re
import logging

import scrapy
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
selenium_logger = logging.getLogger("selenium")
selenium_logger.setLevel(logging.CRITICAL)


class StoreYouwannaSpider(scrapy.Spider):
    name = "youwanna"
    start_urls = ["https://you-wanna.ru/sitemap.xml"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        all_links = bs(response.text, "xml")
        row_items = [i.text for i in all_links.findAll("loc")]
        items = sum(
            list(filter(None, [re.findall(r"https://you-wanna.ru/catalog/.*/product/.*/", i) for i in row_items])), []
        )

        for item_link in items:
            self.driver.get(item_link)
            soup = bs(self.driver.page_source, "lxml")
            self.driver.implicitly_wait(30)
            """
            If the page takes longer than 30 seconds 
            to load, the product is usually out of stock, 
            so I handle this situation with "try-except"
            """
            try:
                item_name = soup.find("div", class_="page_product_heading").text.strip()
                item_price = int(re.sub(r"[^0-9]", "", soup.find("span", class_="standard_price").text))
                item_image = soup.find("div", class_="product_img_wrapper").find("img").get("src")

                yield {
                    "is_available": True,
                    "item_name": item_name,
                    "item_price": item_price,
                    "item_image": item_image,
                    "source_url": item_link,
                }

            except:
                yield dict(is_available=False)

        self.driver.quit()
