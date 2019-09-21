import re

from block import Block
from util import format_price


class Item:
    def __init__(self, desc: Block, price: Block):
        self.desc_block = desc
        self.price_block = price

        self.desc = desc.text
        self.price = format_price(price.text)

    @property
    def json(self):
        return {
            "desc": self.desc,
            "price": self.price,
        }

    def __repr__(self):
        return "<{}:{}>".format(self.desc, self.price)
