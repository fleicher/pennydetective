from block import Block


class Item:
    def __init__(self, desc: Block, price: Block):
        self.desc_block = desc
        self.price_block = price

        self.desc = desc.text
        self.price = price.price

    @property
    def json(self):
        return {
            "desc": self.desc,
            "price": self.price,
        }

    def __repr__(self):
        return "<{}:{}>".format(self.desc, self.price)
