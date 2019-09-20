import math
from typing import NamedTuple, Dict

import matplotlib.figure
import numpy as np
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import get_colors

from receipt import Receipt


class Instance(NamedTuple):
    receipt: Receipt
    expected: Dict
    name: str
    idx: int
    fig: matplotlib.figure.Figure = None
    ax: matplotlib.figure.Axes = None
    w: int = None
    h: int = None

    def draw_angle(self):
        self.ax.arrow(self.w / 2, self.h / 2, math.cos(self.receipt.angle) * self.w / 10,
                      math.sin(self.receipt.angle) * self.h / 10)

    def draw_prices(self):
        x, y = zip(*[price[1] for price in self.receipt.prices])

        self.ax.plot(np.array(x) * self.w, np.array(y) * self.h, "bo")

    def draw_total(self):
        polygon = Polygon(np.array([self.receipt.total_desc[i] for i in range(4)])
                          * np.array([self.w, self.h]), closed=True)
        self.ax.plot(polygon.xy[:, 0], polygon.xy[:, 1], color='#6699cc', alpha=0.7, linewidth=3)
        self.fig.show()

    def draw_columns(self):
        number_of_columns = len(self.receipt.columns)
        colors = [get_colors(i, number_of_columns) for i in range(number_of_columns)]
        for column_idx, column in enumerate(self.receipt.columns):
            x, y = zip(*[price.top_left for price in column.prices])
            self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=colors[column_idx], alpha=0.5)
            x_rot = column.get_rotated_x(self.receipt.angle)
            self.ax.text(x=x_rot * self.w, y=self.h / 10, s="{:.2f}".format(x_rot), c=colors[column_idx])

    def draw_items(self):
        number_items = len(self.receipt.items)
        if number_items == 0:
            print("couldn't find any items")
            return
        colors = [get_colors(i, number_items) for i in range(number_items)]
        x, y = zip(*[item.desc_block[1] for item in self.receipt.items])
        self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=colors, alpha=0.5, edgecolors='b')
        x, y = zip(*[item.price_block[1] for item in self.receipt.items])
        self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=colors, alpha=0.3, edgecolors='b')
        if self.receipt.total is not None and self.receipt.total_desc is not None:
            for block in (self.receipt.total_desc, self.receipt.total.price_block):
                polygon = Polygon(np.array([block[i] for i in range(4)])
                                  * np.array([self.w, self.h]), closed=True)
                self.ax.plot(polygon.xy[:, 0], polygon.xy[:, 1], color='#6699cc', alpha=0.7, linewidth=3)
        self.fig.show()

    def draw(self):
        self.draw_angle()
        self.draw_columns()
        self.draw_items()

    @staticmethod
    def breakpoint():
        print("break")

    def __repr__(self):
        return self.name
