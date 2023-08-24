import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StorePostmeridiemSpider(scrapy.Spider):
    name = "postmeridiem"
    base_url = furl("https://postmeridiem-brand.com/")
    start_urls = ["https://postmeridiem-brand.com/catalog/"]

    def parse(self, response, **kwargs):
        maximum_parsing_pages = self.settings["external_configs"].get("maximum_parsing_pages")
        if maximum_parsing_pages is not None:
            max_page_number = maximum_parsing_pages
        else:
            max_page_number = int(response.css(".catalog__main-show-more-page::text")[-1].get().strip())
        for page_number in range(1, max_page_number + 1):
            page_url = furl(response.url)
            page_url.add(args={"PAGEN_1": page_number})

            yield Request(page_url.url, self._parse_item)

    def _parse_item(self, response):
        for item in response.css(".ui-card2__wrapper"):
            item_image_relative_path = item.css(".ui-card2__img").xpath("@src").get()
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            item_name = item.css('span[itemprop="name"]::text').get().strip()
            item_price = int(re.sub(r"[^0-9]", "", item.css(".price::text").get()))
            source_raw_url = item.css("a").xpath("@href").get()
            source_url = copy.deepcopy(self.base_url)
            source_url.path.add(source_raw_url)

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url,
            }
