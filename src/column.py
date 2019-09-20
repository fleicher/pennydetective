from block import Block
from util import rotate_point, avg


class Column:
    def __init__(self, price: Block):
        self.prices = [price]

    def add(self, price: Block):
        self.prices.append(price)

    def get_rotated_x(self, angle):
        rotated_points = [rotate_point(-angle, price.top_right) for price in self.prices]
        return avg([point[0] for point in rotated_points])

    def __repr__(self):
        return "[{}]".format(";".join([price.text[:6] for price in self.prices[:5]]))
