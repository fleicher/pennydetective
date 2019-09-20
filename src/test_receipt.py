import json
import math
import os
from typing import NamedTuple, Dict
from unittest import TestCase

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from receipt import Receipt


class TestReceipt(TestCase):
    SHOW = True
    IMAGE_PATH = "../data/"
    IMAGES_NAMES = (
        "DSC_3607",  # "DSC_3618", "DSC_3619"
    )

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
            colors = [plt.get_cmap('gist_rainbow')(1. * i / number_of_columns) for i in range(number_of_columns)]

            # x, y = zip(*[price[1] for price in self.receipt.prices])
            # mapped_colors = list(map(lambda i: colors[i], self.receipt.price2column_map))
            # self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=mapped_colors, alpha=0.5)
            # for column_idx, x_rot in enumerate(self.receipt.column_x_rotated):
            #     self.ax.text(x=x_rot * self.w, y=self.h / 10, s="{:.2f}".format(x_rot), c=colors[column_idx])
            for column_idx, column in enumerate(self.receipt.columns):
                x, y = zip(*[price.top_right for price in column.prices])
                self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=colors[column_idx], alpha=0.5)
                x_rot = column.get_rotated_x(self.receipt.angle)
                self.ax.text(x=x_rot * self.w, y=self.h / 10, s="{:.2f}".format(x_rot), c=colors[column_idx])

        def draw_items(self):
            number_items = len(self.receipt.items)
            colors = [plt.get_cmap('gist_rainbow')(1. * i / number_items) for i in range(number_items)]
            mapped_colors = list(map(lambda i: colors[i], range(number_items)))
            x, y = zip(*[item.desc_json[1] for item in self.receipt.items])
            self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=mapped_colors, alpha=0.5, edgecolors='b')
            x, y = zip(*[item.price_json[1] for item in self.receipt.items])
            self.ax.scatter(x=np.array(x) * self.w, y=np.array(y) * self.h, c=mapped_colors, alpha=0.3, edgecolors='b')

            polygon = Polygon(np.array([self.receipt.total_desc[i] for i in range(4)])
                              * np.array([self.w, self.h]), closed=True)
            self.ax.plot(polygon.xy[:, 0], polygon.xy[:, 1], color='#6699cc', alpha=0.7, linewidth=3)
            self.fig.show()

        def draw(self):
            self.draw_angle()
            self.draw_columns()
            self.draw_items()
            self.draw_total()

        @staticmethod
        def breakpoint():
            print("break")

    @classmethod
    def setUpClass(cls) -> None:
        cls.instances = []

        for n, image_name in enumerate(cls.IMAGES_NAMES):
            with open(os.path.join(cls.IMAGE_PATH, image_name, "apiResponse.json")) as f:
                receipt = Receipt(json.load(f))
            with open(os.path.join(cls.IMAGE_PATH, image_name, "result.json")) as f:
                expected = json.load(f)
            fig, ax, w, h = None, None, None, None
            if cls.SHOW:
                im = plt.imread(os.path.join(cls.IMAGE_PATH, image_name, image_name + ".JPG"))
                fig = plt.figure(n)
                ax = fig.add_subplot(111)
                ax.imshow(im)
                h, w, _ = im.shape
            cls.instances.append(cls.Instance(receipt=receipt, expected=expected, name=image_name,
                                              idx=n, fig=fig, ax=ax, w=w, h=h))

    def test_find_writing_angle(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.draw_angle()
            ist.breakpoint()

    def test_find_prices(self):
        for ist in self.instances:
            ist.receipt.find_prices()
            ist.draw_prices()
            ist.breakpoint()

    def test_find_total(self):
        for ist in self.instances:
            ist.receipt.find_total()
            ist.draw_total()
            ist.breakpoint()

    def test_find_columns(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.receipt.find_prices()
            ist.receipt.find_columns()
            ist.draw_columns()
            ist.breakpoint()

    def test_find_items(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.receipt.find_prices()
            ist.receipt.find_columns()
            ist.receipt.find_total()
            ist.receipt.find_items()
            ist.draw_items()
            ist.breakpoint()

    def test_results(self):
        for ist in self.instances:
            ist.receipt.analyze()

            ist.draw()
            ist.breakpoint()

            self.assertEqual(ist.expected["total"], ist.receipt.total)
            self.assertEqual(len(ist.expected["items"]), len(ist.receipt.items))
            for item_expected, item in zip(ist.expected["items"], ist.receipt.items):
                self.assertEqual(item_expected["desc"], item.desc)
                self.assertAlmostEqual(item_expected["price"], item.price)

