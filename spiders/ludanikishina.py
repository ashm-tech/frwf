import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreLudanikishinaSpider(scrapy.Spider):
    name = "ludanikishina"
    p = {
        "accept": "*/*",
        "user-agent": "parser ashm.tech",
    }

    def start_requests(self):
        start_url = "https://ludanikishina.com/categories/82581-katalog"

        yield Request(url=start_url, headers=self.p, callback=self.parse, method="GET")

    def parse(self, response, **kwargs):
        for item_url in response.css(".b-item__info").xpath("@href").getall():
            yield Request(url=item_url, headers=self.p, callback=self._parse_item_page, method="GET")

    def _parse_item_page(self, response):
        item_image = response.css('meta[property="og:image"]').xpath("@content").get()
        item_name = response.css('meta[itemprop="name"]').xpath("@content").get()
        item_price = int(response.css('meta[itemprop="price"]').xpath("@content").get()) // 100

        yield {
            "is_available": True,
            "item_name": item_name,
            "item_price": item_price,
            "item_image": item_image,
            "source_url": response.url,
        }
