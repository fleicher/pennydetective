import json
import os
from typing import List
from unittest import TestCase

import matplotlib.pyplot as plt

from instance import Instance
from receipt import Receipt


class TestReceipt(TestCase):
    SHOW = True
    IMAGE_PATH = "../data/"
    IMAGES_NAMES = (
        "3460", "8507", "kassenbon-1", "Nubon", "nudelhusli", "QR",
        "DSC_3607", "DSC_3618", "DSC_3619"
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.instances: List[Instance] = []

        for n, image_name in enumerate(cls.IMAGES_NAMES):
            with open(os.path.join(cls.IMAGE_PATH, image_name, "apiResponse.json")) as f:
                receipt = Receipt(json.load(f))
            with open(os.path.join(cls.IMAGE_PATH, image_name, "result.json")) as f:
                expected = json.load(f)

            im = None if not cls.SHOW else plt.imread(os.path.join(cls.IMAGE_PATH,  image_name,
                                                                   "image.jpg"))

            cls.instances.append(Instance(receipt=receipt, expected=expected, name=image_name,
                                          idx=n, im=im))

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

            self.assertEqual(ist.expected["total"], ist.receipt.total.price)
            self.assertEqual(len(ist.expected["items"]), len(ist.receipt.items))
            for item_expected, item in zip(ist.expected["items"], ist.receipt.items):
                self.assertEqual(item_expected["desc"], item.desc)
                self.assertAlmostEqual(item_expected["price"], item.price)
