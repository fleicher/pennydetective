import numpy as np

from util import rotate_point, format_price


class Block:

    def __init__(self, block_json, receipt):
        self.json = block_json
        self.receipt = receipt

        self.id = block_json["Id"]
        self.conf = block_json["Confidence"]
        self.poly = np.array([(p["X"], p["Y"]) for p in block_json["Geometry"]["Polygon"]])
        self.text = block_json["Text"]
        self.bb = block_json["Geometry"]["BoundingBox"]
        self.type = block_json["BlockType"]

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
    def left_center_rot(self):
        return rotate_point(self.receipt.angle, self.left_center)

    @property
    def top_center_rot(self):
        top_center = (self.top_left + self.top_right) / 2
        return rotate_point(self.receipt.angle, top_center)

    @property
    def right_center_rot(self):
        right_center = (self.top_right + self.bottom_right) / 2
        return rotate_point(self.receipt.angle, right_center)

    @property
    def bottom_center_rot(self):
        bottom_center = (self.bottom_left + self.bottom_right) / 2
        return rotate_point(self.receipt.angle, bottom_center)

    @property
    def center_rot(self):
        center = (self.top_left + self.top_right + self.bottom_right + self.bottom_left) / 4
        return rotate_point(self.receipt.angle, center)

    @property
    def price(self):
        return format_price(self.text)

    def __repr__(self):
        return "<'{}' ({})>".format(self.text, hash(self))

