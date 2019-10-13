import json
import os
from typing import List
from unittest import TestCase

import matplotlib.pyplot as plt

from instance import Instance
from receipt import Receipt


class TestReceipt(TestCase):
    SHOW = True
    DATA_PATH = "../data/"
    IMAGES_NAMES = (
        "dm2", "edeka1", "edeka2",
        # "hm", "hm2",
        "rewe1", "rewe2",
        # "3460", "8507", "kassenbon-1", "Nubon", "QR",
        # "DSC_3607", "DSC_3618", "DSC_3619",
    )

    @classmethod
    def setUpClass(cls):
        cls.instances: List[Instance] = []
        for name in cls.IMAGES_NAMES:
            with open(os.path.join(cls.DATA_PATH, name, "apiResponse.json")) as f:
                receipt = Receipt(json.load(f), name=name)
            with open(os.path.join(cls.DATA_PATH, name, "result.json")) as f:
                expected = json.load(f)

            im = None if not cls.SHOW else plt.imread(os.path.join(cls.DATA_PATH, name, "image.jpg"))
            cls.instances.append(Instance(receipt=receipt, expected=expected, im=im))

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
        number_correct = 0
        for ist in self.instances:
            is_correct = True
            ist.receipt.analyze()
            ist.draw()

            is_correct &= ist.expected["total"] == ist.receipt.total.price
            same_length = len(ist.expected["items"]) == len(ist.receipt.items)
            is_correct &= same_length
            if same_length:
                for n, (item_expected, item) in enumerate(zip(ist.expected["items"], ist.receipt.items)):
                    if item_expected["desc"] != item.desc or item_expected["price"] != item.price:
                        print("[{}] #{} <'{}': {}> != <'{}': {}>".format(
                            ist.name, n, item_expected["desc"], item_expected["price"], item.desc, item.price
                        ))
                        is_correct = False
            number_correct += is_correct
            print("[{}] Result: {}, Length: {}".format(
                ist.receipt.name, is_correct, same_length))
            pass
        self.assertEqual(number_correct, len(self.instances))
