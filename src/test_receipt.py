import json
import math
import os
from typing import NamedTuple, Dict
from unittest import TestCase

import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from receipt import Receipt


class TestReceipt(TestCase):
    SHOW = True
    IMAGE_PATH = "../data/"
    IMAGES_NAMES = (
        "DSC_3605",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.instances = []

        class Instance(NamedTuple):
            receipt: Receipt
            expected: Dict
            name: str
            idx: int
            fig: matplotlib.figure.Figure = None
            ax: matplotlib.figure.Axes = None
            w: int = None
            h: int = None

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
            cls.instances.append(Instance(receipt=receipt, expected=expected, name=image_name,
                                          idx=n, fig=fig, ax=ax, w=w, h=h))

    def test_find_writing_angle(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.ax.arrow(ist.w / 2, ist.h / 2, math.cos(ist.receipt.angle) * ist.w / 10,
                         math.sin(ist.receipt.angle) * ist.h / 10)

    def test_find_prices(self):
        for ist in self.instances:
            ist.receipt.find_prices()
            if TestReceipt.SHOW:
                x, y = zip(*[Receipt.get_bound_of_word(price) for price in ist.receipt.prices])

                ist.ax.plot(np.array(x) * ist.w, np.array(y) * ist.h, "bo")
            self.assertTrue(True)

    def test_find_total(self):
        for ist in self.instances:
            ist.receipt.find_total()
            if TestReceipt.SHOW:
                polygon = Polygon(np.array([Receipt.get_bound_of_word(ist.receipt.total_desc, i)
                                            for i in range(4)]) * np.array([ist.w, ist.h]), closed=True)
                ist.ax.plot(polygon.xy[:, 0], polygon.xy[:, 1], color='#6699cc', alpha=0.7, linewidth=3)

    def test_find_columns(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.receipt.find_prices()
            ist.receipt.find_columns()
            if TestReceipt.SHOW:
                number_of_columns = len(set(ist.receipt.price2column_map))
                colors = [plt.get_cmap('gist_rainbow')(1. * i / number_of_columns) for i in range(number_of_columns)]

                x, y = zip(*[Receipt.get_bound_of_word(price) for price in ist.receipt.prices])
                mapped_colors = list(map(lambda i: colors[i], ist.receipt.price2column_map))
                ist.ax.scatter(x=np.array(x) * ist.w, y=np.array(y) * ist.h, c=mapped_colors, alpha=0.5)
                for column_idx, x_rot in enumerate(ist.receipt.column_x_rotated):
                    ist.ax.text(x=x_rot * ist.w, y=ist.h / 10, s="{:.2f}".format(x_rot), c=colors[column_idx])
            self.assertTrue(True)

    def test_find_items(self):
        for ist in self.instances:
            ist.receipt.find_writing_angle()
            ist.receipt.find_prices()
            ist.receipt.find_columns()
            ist.receipt.find_total()
            ist.receipt.find_items()
            if TestReceipt.SHOW:
                number_items = len(ist.receipt.items)
                colors = [plt.get_cmap('gist_rainbow')(1. * i / number_items) for i in range(number_items)]
                mapped_colors = list(map(lambda i: colors[i], range(number_items)))
                x, y = zip(*[Receipt.get_bound_of_word(item.desc_json) for item in ist.receipt.items])
                ist.ax.scatter(x=np.array(x) * ist.w, y=np.array(y) * ist.h, c=mapped_colors, alpha=0.5)
                x, y = zip(*[Receipt.get_bound_of_word(item.price_json) for item in ist.receipt.items])
                ist.ax.scatter(x=np.array(x) * ist.w, y=np.array(y) * ist.h, c=mapped_colors, alpha=0.3)

                polygon = Polygon(np.array([Receipt.get_bound_of_word(ist.receipt.total_json, i)
                                            for i in range(4)]) * np.array([ist.w, ist.h]), closed=True)
                ist.ax.plot(polygon.xy[:, 0], polygon.xy[:, 1], color='#6699cc', alpha=0.7, linewidth=3)

    def test_results(self):
        for ist in self.instances:
            ist.receipt.analyze()

            self.assertEqual(ist.expected["total"], ist.receipt.total)
            self.assertEqual(len(ist.expected["items"]), len(ist.receipt.items))
            for item_expected, item in zip(ist.expected["items"], ist.receipt.items):
                self.assertEqual(item_expected["desc"], item.desc)
                self.assertAlmostEqual(item_expected["price"], item.price)
