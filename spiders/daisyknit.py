import re
import copy
import logging

import scrapy
from furl import furl
from scrapy.http import FormRequest

logger = logging.getLogger(__name__)


class StoreDaisyknitSpider(scrapy.Spider):
    name = "daisyknit"
    base_url = furl("https://daisyknit.ru/")

    def start_requests(self):
        categoryes = [
            "platya_1",
            "kostyumy_1",
            "zhakety_i_zhilety",
            "bryuki_i_shorty",
            "futbolki_i_tonkiy_trikotazh",
            "denim",
            "rubashki_i_bluzy",
            "yubki_1",
            "topy",
            "obuv_2",
            "sumki_i_aksessuary",
        ]

        for category in categoryes:
            params = {
                "params[CATALOG_IBLOCK_ID]": "2",
                "params[SECTION_ID]": "",
                "params[SECTION_CODE]": category,
                "params[CATALOG_FIELD_CODE][0]": "EXTERNAL_ID",
                "params[CATALOG_FIELD_CODE][1]": "SORT",
                "params[CATALOG_FIELD_CODE][2]": "NAME",
                "params[CATALOG_FIELD_CODE][3]": "IBLOCK_SECTION_ID",
                "params[CATALOG_FIELD_CODE][4]": "DETAIL_PAGE_URL",
                "params[SKU_IBLOCK_ID]": "3",
                "params[SKU_FIELD_CODE][0]": "EXTERNAL_ID",
                "params[SKU_FIELD_CODE][1]": "SORT",
                "params[SKU_FIELD_CODE][2]": "NAME",
                "params[SKU_PROPERTY_CODE][0]": "ID_POISK",
                "params[SKU_PROPERTY_CODE][1]": "ADD_IN_CATALOG",
                "params[SKU_PROPERTY_CODE][2]": "RAZMERY",
                "params[SKU_PROPERTY_CODE][3]": "TSVET_DLYA_SAYTA",
                "params[SKU_PROPERTY_CODE][4]": "ALT_SORT",
                "params[SKU_PROPERTY_CODE][5]": "MORE_PHOTO",
                "params[SKU_PROPERTY_CODE][6]": "HOVER_PHOTO",
                "params[SKU_PROPERTY_CODE][7]": "SECTION_SOON",
                "params[SKU_PROPERTY_CODE][8]": "TSVET",
                "params[SECTION_WEEK_CHECK]": "Y",
                "params[ALT_SORT_CHECK]": "Y",
                "params[IN_STOCK_CHECK]": "Y",
                "params[FILTER]": "Y",
                "params[FILTER_CATALOG_FIELD_CODE][0]": "",
                "params[FILTER_SKU_PROPERTY_CODE][0]": "RAZMERY",
                "params[FILTER_SKU_PROPERTY_CODE][1]": "TSVET_DLYA_SAYTA",
                "params[FILTER_DISCOUNT]": "N",
                "params[FILTER_IN_STOCK]": "Y",
                "params[PORTION]": "12",
                "params[SPECIAL_SECTION]": "",
                "params[CACHE_TYPE]": "A",
                "params[~CATALOG_IBLOCK_ID]": "2",
                "params[~SECTION_ID]": "",
                "params[~SECTION_CODE]": "platya_1",
                "params[~CATALOG_FIELD_CODE][0]": "EXTERNAL_ID",
                "params[~CATALOG_FIELD_CODE][1]": "SORT",
                "params[~CATALOG_FIELD_CODE][2]": "NAME",
                "params[~CATALOG_FIELD_CODE][3]": "IBLOCK_SECTION_ID",
                "params[~CATALOG_FIELD_CODE][4]": "DETAIL_PAGE_URL",
                "params[~SKU_IBLOCK_ID]": "3",
                "params[~SKU_FIELD_CODE][0]": "EXTERNAL_ID",
                "params[~SKU_FIELD_CODE][1]": "SORT",
                "params[~SKU_FIELD_CODE][2]": "NAME",
                "params[~SKU_PROPERTY_CODE][0]": "ID_POISK",
                "params[~SKU_PROPERTY_CODE][1]": "ADD_IN_CATALOG",
                "params[~SKU_PROPERTY_CODE][2]": "RAZMERY",
                "params[~SKU_PROPERTY_CODE][3]": "TSVET_DLYA_SAYTA",
                "params[~SKU_PROPERTY_CODE][4]": "ALT_SORT",
                "params[~SKU_PROPERTY_CODE][5]": "MORE_PHOTO",
                "params[~SKU_PROPERTY_CODE][6]": "HOVER_PHOTO",
                "params[~SKU_PROPERTY_CODE][7]": "SECTION_SOON",
                "params[~SKU_PROPERTY_CODE][8]": "TSVET",
                "params[~SECTION_WEEK_CHECK]": "Y",
                "params[~ALT_SORT_CHECK]": "Y",
                "params[~IN_STOCK_CHECK]": "Y",
                "params[~FILTER]": "Y",
                "params[~FILTER_CATALOG_FIELD_CODE][0]": "",
                "params[~FILTER_SKU_PROPERTY_CODE][0]": "RAZMERY",
                "params[~FILTER_SKU_PROPERTY_CODE][1]": "TSVET_DLYA_SAYTA",
                "params[~FILTER_DISCOUNT]": "N",
                "params[~FILTER_IN_STOCK]": "Y",
                "params[~PORTION]": "12",
                "params[~SPECIAL_SECTION]": "",
                "params[~CACHE_TYPE]": "A",
                "request[filter]": "Y",
            }
            """
            Without all the parameters, 
            the request works out clumsily 
            and the data deteriorates, 
            it is unrealistic to parse 
            the site by simple parsing
            """
            yield FormRequest(
                url="https://daisyknit.ru/local/components/webstripe/main.catalog/ajax.php",
                callback=self.parse,
                formdata=params,
                method="POST",
            )

    def parse(self, response, **kwargs):
        items = response.json()["OFFERS"]
        for item in items:
            item_name = item["PARENT_FIELDS"]["NAME"]
            item_price = item["PRICE"]
            item_image_relative_path = item["PROPERTIES"]["MORE_PHOTO"]["VALUE"]
            item_image = copy.deepcopy(self.base_url)
            item_image.path.add(item_image_relative_path)
            source_url = furl("https://daisyknit.ru" + item["PARENT_FIELDS"]["DETAIL_PAGE_URL"])
            source_url.add(args={"sku": item["PARENT_FIELDS"]["ID"]})

            yield {
                "is_available": True,
                "item_name": item_name,
                "item_price": item_price,
                "item_image": item_image.url,
                "source_url": source_url.url,
            }
