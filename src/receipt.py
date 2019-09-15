import math
import re
from typing import List, Set, Dict

import numpy as np
from fuzzywuzzy import fuzz

from item import Item
from util import get_angle, get_abs_perp_angle_diff, rotate_point, get_dist_to_line, \
    format_price


class Receipt:
    REGEX = r"\d+(\.|,)\d\d"
    TOTAL_WORDS = ("total", "summe", "suma", "zu zahlen", "pagar", "zwischensumme")
    TOTAL_THRESHOLD = 65
    COLUMN_ANGLE_TRESHOLD = math.pi / 8
    ROW_DIST_THRESHOLD = 0.05
    COLUMN_SEPARATOR_THRESHOLD = 0.2

    def __init__(self, data):
        self.data = data
        self.bounds = None
        self.prices: List[Dict] = []
        self.price2column_map: List[int] = []
        self.angle: float = 0
        self.column_x_rotated = None
        self.items: List[Item] = []
        self.total_desc = self.total_json = self.total = None

    def analyze(self):
        self.find_writing_angle()
        self.find_prices()
        self.find_columns()
        self.find_total()
        self.find_items()

    def find_writing_angle(self):
        """
        take <=30 lines from the receipt and determine the angle of writing
        """
        angles = []
        for line in [self.lines[i] for i in range(0, len(self.lines), len(self.lines) // 30)]:
            point_top_left = self.get_bound_of_word(line, 0)
            point_top_right = self.get_bound_of_word(line, 1)
            angles.append(get_angle(point_top_left, point_top_right))
        self.angle = sum(angles) / len(angles)
        return angles

    def find_prices(self):
        """
        go through all words, find the ones that match our number format
        if you can put the ending of three or more in good line we have found the right side.
        always take three consecutive numbers and store their lines
        the ones that fit together the best are our line!
        """
        pattern = re.compile(Receipt.REGEX)
        self.prices = [word for word in self.words if pattern.match(word["Text"])]

    def find_total(self):
        current_total_json = None
        current_total_ratio = 0
        for word in self.words:
            ratio = max([fuzz.ratio(word["Text"].lower(), total_word) for total_word in Receipt.TOTAL_WORDS])
            if ratio > current_total_ratio and ratio > Receipt.TOTAL_THRESHOLD:
                current_total_ratio = ratio
                current_total_json = word
        if current_total_json is not None:
            print("Found Total: {}".format(current_total_json["Text"]))
            self.total_desc = current_total_json

    def find_columns(self):
        not_mapped_prices: Set[int] = set(range(len(self.prices)))  # list(enumerate(self.prices))
        self.price2column_map: List = [None] * len(self.prices)
        column_counter = 0
        while len(not_mapped_prices) > 0:
            idx1 = sorted(not_mapped_prices).pop(0)
            not_mapped_prices.remove(idx1)
            point1 = Receipt.get_bound_of_word(self.prices[idx1])
            self.price2column_map[idx1] = column_counter
            for idx2 in sorted(not_mapped_prices):
                point2 = Receipt.get_bound_of_word(self.prices[idx2])
                angle = get_angle(point1, point2)
                if get_abs_perp_angle_diff(self.angle, angle) < self.COLUMN_ANGLE_TRESHOLD:
                    not_mapped_prices.remove(idx2)
                    self.price2column_map[idx2] = column_counter
            column_counter += 1

        column_x_rotated_list = [[] for _ in range(column_counter)]
        for price_idx, price in enumerate(self.prices):
            point = Receipt.get_bound_of_word(price)
            x_rot, _ = rotate_point(self.angle, point)
            column_x_rotated_list[self.price2column_map[price_idx]].append(x_rot)
        self.column_x_rotated = [
            sum(column_x_rotated_list[column_idx]) / len(column_x_rotated_list[column_idx])
            for column_idx in range(column_counter)
        ]

    def find_items(self):
        right_most_column_index = int(np.argmax(self.column_x_rotated))
        total_height = 1.0
        current_total_price_min_descr = total_desc_right_center_point = total_desc_right_center_point_rotated = None
        current_total_price_min_dist = math.sqrt(2)
        if self.total_desc is not None:
            total_desc_right_center_point = (Receipt.get_bound_of_word(self.total_desc, 1)
                                             + Receipt.get_bound_of_word(self.total_desc, 2)) / 2
            _, total_height = rotate_point(self.angle, total_desc_right_center_point)
            total_desc_right_center_point_rotated = rotate_point(self.angle, total_desc_right_center_point)

        for price_idx, price in enumerate(self.prices):
            price_left_center_point = (Receipt.get_bound_of_word(price, 0) + Receipt.get_bound_of_word(price, 3)) / 2
            price_right_center_point = (Receipt.get_bound_of_word(price, 1) + Receipt.get_bound_of_word(price, 2)) / 2
            price_left_center_point_rotated = rotate_point(self.angle, price_left_center_point)

            # check how close it is 'TOTAL' label
            if total_desc_right_center_point is not None:
                dist_to_current_price = get_dist_to_line(
                    (0, total_height), (0.1, total_height), price_left_center_point_rotated)
                if dist_to_current_price < current_total_price_min_dist and \
                        total_desc_right_center_point_rotated[1] < price_left_center_point_rotated[1]:
                    current_total_price_min_dist = dist_to_current_price
                    current_total_price_min_descr = price

            if self.price2column_map[price_idx] != right_most_column_index:
                continue
            if rotate_point(self.angle, Receipt.get_bound_of_word(price, 3))[1] > total_height:
                continue
            # calculate center of price.
            associated_lines = []
            for line in self.lines:
                center_point = sum([Receipt.get_bound_of_word(line, i) for i in range(4)]) / 4
                dist = get_dist_to_line(price_left_center_point, price_right_center_point, center_point)
                if dist > Receipt.ROW_DIST_THRESHOLD:
                    continue
                center_point_rotated = rotate_point(self.angle, center_point)
                if center_point_rotated[0] + Receipt.COLUMN_SEPARATOR_THRESHOLD > price_left_center_point_rotated[0]:
                    continue

                associated_lines.append((dist, line))
                # calculate center of itemline
                # difference of this center to ray from price.

            if len(associated_lines) > 0:
                desc = sorted(associated_lines, key=lambda l: l[0])[0]
                self.items.append(Item(desc[1], price))

        if current_total_price_min_descr is not None:
            self.total_json = current_total_price_min_descr
            self.total = format_price(current_total_price_min_descr["Text"])

    def group(self):
        for block in self.data["Blocks"]:
            if block["BlockType"] != "LINE":
                continue
            if block["Geometry"]["BoundingBox"]["Top"] > self.bounds["top"]:
                pass

    @property
    def words(self):
        return self._get_blocks_of_type("WORD")

    @property
    def lines(self):
        return self._get_blocks_of_type("LINE")

    def _get_blocks_of_type(self, type_="LINE"):
        return [block for block in self.data["Blocks"] if block["BlockType"] == type_]

    @staticmethod
    def get_bound_of_word(word, position: int = 1):
        return np.array((word["Geometry"]["Polygon"][position]["X"], word["Geometry"]["Polygon"][position]["Y"]))
