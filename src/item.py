import re

from block import Block
from util import format_price


class Item:
    def __init__(self, desc: Block, price: Block):
        self.desc_json = desc
        self.price_json = price

        self.desc = desc.text
        self.price = format_price(price.text)

    def __repr__(self):
        return "<{}:{}>".format(self.desc, self.price)
