from typing import Dict

import numpy as np

from util import format_price


class Block:

    def __init__(self, block_json: Dict):
        self.json = block_json

        self.id: str = block_json["Id"]
        self.conf = float(block_json["Confidence"])
        self.poly = np.array([(p["X"], p["Y"]) for p in block_json["Geometry"]["Polygon"]])
        self.text: str = block_json["Text"]
        self.bb: Dict = block_json["Geometry"]["BoundingBox"]
        self.type: str = block_json["BlockType"]

        self.is_price = False
        self.price_column = None
        self.linked_description, self.linked_price = None, None

    def __getitem__(self, no):
        return self.poly[no]

    @property
    def top_left(self):
        return self[0]

    @property
    def top_right(self):
        return self[1]

    @property
    def bottom_right(self):
        return self[2]

    @property
    def bottom_left(self):
        return self[3]

    @property
    def left_center(self):
        return (self.top_left + self.bottom_left) / 2

    @property
    def right_center(self):
        return (self.top_right + self.bottom_right) / 2

    @property
    def center(self) -> np.ndarray:
        return (self.left_center + self.right_center) / 2

    @property
    def price(self):
        return format_price(self.text)

    def __repr__(self):
        return "'{}'".format(self.text)
