import re

from util import format_price


class Item:
    def __init__(self, desc_json, price_json):
        self.desc_json = desc_json
        self.price_json = price_json

        self.desc = desc_json["Text"]
        self.price = format_price(price_json["Text"])
