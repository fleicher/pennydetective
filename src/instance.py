import math
from typing import Dict, Optional

import matplotlib.figure
import numpy as np
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt


from receipt import Receipt


class Instance:

    def __init__(self, receipt: Receipt, expected: Dict, name: str, idx: int,
                 im: Optional[np.ndarray] = None):
        self.receipt = receipt
        self.expected = expected
        self.name = name
        self.idx = idx
        self.im = im
        self._fig, self._ax, self._w, self._h = None, None, None, None

    @property
    def fig(self):
        self._create_fig_if_necessary()
        return self._fig

    @property
    def ax(self):
        self._create_fig_if_necessary()
        return self._ax

    @property
    def w(self):
        self._create_fig_if_necessary()
        return self._w

    @property
    def h(self):
        self._create_fig_if_necessary()
        return self._h

    def _create_fig_if_necessary(self):
        if self._fig is not None:
            return
        if self.im is None:
            raise ValueError("No value for parameter 'im' was set")
        self._fig: matplotlib.figure.Figure = plt.figure(self.idx)
        self._ax: matplotlib.figure.Axes = self._fig.add_subplot(111)
        self._ax.imshow(self.im)
        self._h: float = self.im.shape[0]
        self._w: float = self.im.shape[1]

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
        colors = [get_color(i, number_of_columns) for i in range(number_of_columns)]
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
        x, y = zip(*[item.desc_block[1] for item in self.receipt.items])
        self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=get_colors(number_items),
                        alpha=0.5, edgecolors='b')
        x, y = zip(*[item.price_block[1] for item in self.receipt.items])
        self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=get_colors(number_items),
                        alpha=0.3, edgecolors='b')
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


def get_color(i: int, n: int) -> np.ndarray:
    """ creates a rainbow, gives color #i (0-indexed) of n colors"""
    return np.array(plt.get_cmap('gist_rainbow')(1. * i / n)).reshape(1, -1)


def get_colors(n: int) -> np.ndarray:
    """ creates a rainbow, gives n colors"""
    return np.stack([get_color(i, n) for i in range(n)]).reshape(n, -1)
