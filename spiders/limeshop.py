import logging

import scrapy
from scrapy.http import Request

logger = logging.getLogger(__name__)


class StoreLimeshopSpider(scrapy.Spider):
    name = "limeshop"
    start_urls = [
        "https://lime-shop.com/api/section/sumki?page=1&size=1000",
        "https://lime-shop.com/api/section/crochet_festival?page=1&size=1000",
        "https://lime-shop.com/api/section/denim?page=1&size=1000",
        "https://lime-shop.com/api/section/boho_voyage?page=1&size=1000",
        "https://lime-shop.com/api/section/bestsellers?page=1&size=1000",
        "https://lime-shop.com/api/section/basic_wardrobe?page=1&size=1000",
        "https://lime-shop.com/api/section/platya?page=1&size=1000",
        "https://lime-shop.com/api/section/blazers?page=1&size=1000",
        "https://lime-shop.com/api/section/bryuki?page=1&size=1000",
        "https://lime-shop.com/api/section/suit?page=1&size=1000",
        "https://lime-shop.com/api/section/kurtki?page=1&size=1000",
        "https://lime-shop.com/api/section/futbolki?page=1&size=1000",
        "https://lime-shop.com/api/section/dzhinsy?page=1&size=1000",
        "https://lime-shop.com/api/section/shirts_and_blouses?page=1&size=1000",
        "https://lime-shop.com/api/section/yubki?page=1&size=1000",
        "https://lime-shop.com/api/section/topy?page=1&size=1000",
        "https://lime-shop.com/api/section/shorty?page=1&size=1000",
        "https://lime-shop.com/api/section/co_ord_sets?page=1&size=1000",
        "https://lime-shop.com/api/section/tolstovki?page=1&size=1000",
        "https://lime-shop.com/api/section/sportswear?page=1&size=1000",
        "https://lime-shop.com/api/section/body_basics?page=1&size=1000",
        "https://lime-shop.com/api/section/tricotash?page=1&size=1000",
        "https://lime-shop.com/api/section/palto_i_trench?page=1&size=1000",
        "https://lime-shop.com/api/section/last_sizes?page=1&size=1000",
        "https://lime-shop.com/api/section/underwear_invisible?page=1&size=1000",
        "https://lime-shop.com/api/section/underwear_seamless?page=1&size=1000",
        "https://lime-shop.com/api/section/underwear_microfiber?page=1&size=1000",
        "https://lime-shop.com/api/section/underwear?page=1&size=1000",
        "https://lime-shop.com/api/section/bralettes?page=1&size=1000",
        "https://lime-shop.com/api/section/briefs?page=1&size=1000",
        "https://lime-shop.com/api/section/bodysuits?page=1&size=1000",
        "https://lime-shop.com/api/section/accessories?page=1&size=1000",
        "https://lime-shop.com/api/section/hats?page=1&size=1000",
        "https://lime-shop.com/api/section/sunglasses?page=1&size=1000",
        "https://lime-shop.com/api/section/belts?page=1&size=1000",
        "https://lime-shop.com/api/section/bijouterie?page=1&size=1000",
        "https://lime-shop.com/api/section/all_shoes?page=1&size=1000",
        "https://lime-shop.com/api/section/sandals?page=1&size=1000",
        "https://lime-shop.com/api/section/trainers?page=1&size=1000",
        "https://lime-shop.com/api/section/loafers?page=1&size=1000",
        "https://lime-shop.com/api/section/shoes?page=1&size=1000",
    ]

    def parse(self, response, **kwargs):
        table = response.json()["items"]
        for product in table:
            item_name = product["cells"][0]["entity"]["name"]
            item_price = int(product["cells"][0]["entity"]["models"][0]["skus"][0]["price"])
            item_image = product["cells"][0]["entity"]["models"][0]["photo"]["url"]
            entity = product["cells"][0]["entity"]["code"]
            model = product["cells"][0]["entity"]["models"][0]["code"]
            source_url = f"https://lime-shop.com/ru_ru/product/{entity}-{model}"

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image,
                "source_url": source_url,
            }
