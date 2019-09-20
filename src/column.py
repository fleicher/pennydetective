from block import Block
from util import rotate_point, avg


class Column:
    def __init__(self, price: Block):
        self.prices = [price]

    def add(self, price: Block):
        self.prices.append(price)

    def get_rotated_x(self, angle):
        return avg([rotate_point(angle, price.top_right)[0] for price in self.prices])
