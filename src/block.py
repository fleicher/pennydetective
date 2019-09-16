import numpy as np

from util import rotate_point


class Block:

    def __init__(self, block_json):
        self.json = block_json

        self.id = block_json["Id"]
        self.conf = block_json["Confidence"]
        self.poly = np.array([(p["X"], p["Y"]) for p in block_json["Geometry"]["Polygon"]])
        self.text = block_json["Text"]
        self.bb = block_json["Geometry"]["BoundingBox"]
        self.type = block_json["BlockType"]

        self.is_price = False
        self.linked_description, self.linked_price = None, None

    def get_corner(self, no=1):
        return self.poly[no]

    @property
    def top_left(self):
        return self.get_corner(0)

    @property
    def top_right(self):
        return self.get_corner(1)

    @property
    def bottom_right(self):
        return self.get_corner(2)

    @property
    def bottom_left(self):
        return self.get_corner(3)

    def left_center_rot(self, angle):
        left_center = (self.top_left + self.bottom_left) / 2
        return rotate_point(angle, left_center)

    def top_center_rot(self, angle):
        top_center = (self.top_left + self.top_right) / 2
        return rotate_point(angle, top_center)

    def right_center_rot(self, angle):
        right_center = (self.top_right + self.bottom_right) / 2
        return rotate_point(angle, right_center)

    def bottom_center_rot(self, angle):
        bottom_center = (self.bottom_left + self.bottom_right) / 2
        return rotate_point(bottom_center, angle)

    def center_rot(self, angle):
        center = (self.top_left + self.top_right + self.bottom_right + self.bottom_left) / 4
        return rotate_point(center, angle)
