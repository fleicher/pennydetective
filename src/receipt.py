import math
import re
from typing import List, Tuple, Union

import numpy as np
from fuzzywuzzy import fuzz

from block import Block
from column import Column
from item import Item
from util import get_angle, get_abs_perp_angle_diff, rotate_point, get_dist_to_line


class Receipt:
    REGEX = r"\d+(\.|,)\d\d"
    TOTAL_WORDS = ("total", "zu zahlen", "pagar", "zwischensumme", "summe", "suma",)
    TOTAL_THRESHOLD = 65
    COLUMN_ANGLE_TRESHOLD = math.pi / 8
    ROW_DIST_THRESHOLD = 0.05
    COLUMN_SEPARATOR_THRESHOLD = 0.2

    def __init__(self, data, name=None):
        self.data = data

        self.lines: List[Block] = []
        self.words: List[Block] = []
        self.prices: List[Block] = []
        self.columns: List[Column] = []
        self.total_desc: Union[None, Block] = None
        self.angle: float = 0

        self.name = name
        self.items: List[Item] = []
        self.total: Union[Item, None] = None

        for block_json in self.data["Blocks"]:
            if block_json["BlockType"] == "LINE":
                self.lines.append(Block(block_json))
            elif block_json["BlockType"] == "WORD":
                self.words.append(Block(block_json))

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
        LINE_SAMPLE_SIZE = 30
        some_lines = self.lines if len(self.lines) <= LINE_SAMPLE_SIZE else [
            self.lines[i] for i in range(0, len(self.lines), len(self.lines) // 30)]
        angles = [get_angle(line.top_left, line.top_right) for line in some_lines]
        self.angle = sum(angles) / len(angles)
        return self.angle

    def find_prices(self):
        """
        go through all words, find the ones that match our number format
        if you can put the ending of three or more in good line we have found the right side.
        always take three consecutive numbers and store their lines
        the ones that fit together the best are our line!
        """

        pattern = re.compile(Receipt.REGEX)
        # self.prices = [word for word in self.words_json if pattern.match(word["Text"])]
        self.prices = []
        for word in self.words:
            if pattern.match(word.text):
                self.prices.append(word)
                word.is_price = True

    def find_total(self):
        current_total: Union[Block, None] = None
        current_total_ratio = 0
        for total_word in Receipt.TOTAL_WORDS:
            for word in self.words:
                ratio = fuzz.ratio(word.text.lower(), total_word)
                if ratio > current_total_ratio and ratio > Receipt.TOTAL_THRESHOLD:
                    current_total_ratio = ratio
                    current_total = word
            if current_total is not None:
                # iterate through TOTAL words by priority if the first one is found -> break.
                break
        if current_total is not None:
            # print("Found Total: {}".format(current_total.text))
            self.total_desc = current_total

    def find_columns(self):
        undone_prices = self.prices.copy()
        while len(undone_prices) > 0:
            price1 = undone_prices.pop(0)
            column = Column(price1)
            for price2 in undone_prices.copy():
                angle = get_angle(price1.top_right, price2.top_right)
                if get_abs_perp_angle_diff(self.angle, angle) < self.COLUMN_ANGLE_TRESHOLD:
                    undone_prices.remove(price2)
                    column.add(price2)
            self.columns.append(column)

    def find_items(self):
        total_height = 1.0
        if self.total_desc is not None:
            _, total_height = self.r(self.total_desc.right_center)
            total_distances = [(get_dist_to_line((0, total_height), (0.1, total_height),
                                                 self.r(price.left_center)), price) for price in self.prices]
            self.total = Item(self.total_desc, min(total_distances, key=lambda x: x[0])[1])

        right_column = max(self.columns, key=lambda c: c.get_rotated_x(self.angle))
        for price in right_column.prices:
            if self.r(price.bottom_left)[1] > total_height:
                continue  # this price is below the total sum

            associated_desc_for_this_price: List[Tuple[float, Block]] = []
            for line in self.lines:
                dist = get_dist_to_line(price.left_center, price.right_center, line.center)
                if dist > Receipt.ROW_DIST_THRESHOLD:
                    continue  # don't consider a desc that is farther away from this price than the threshold
                if self.r(line.center)[0] + Receipt.COLUMN_SEPARATOR_THRESHOLD > self.r(price.left_center)[0]:
                    continue  # minimum distance between desc and price not > COLUMN_SEPARATOR_THRESHOLD

                associated_desc_for_this_price.append((dist, line))
                # calculate center of item line
                # difference of this center to ray from price.

            if len(associated_desc_for_this_price) > 0:
                best_matching_desc = sorted(associated_desc_for_this_price, key=lambda l: l[0])[0][1]
                self.items.append(Item(best_matching_desc, price))
            else:
                print("could not associate price {} with any description".format(price.text))

    def get_json(self):
        result = {
            "total": None if self.total is None else self.total.price,
            "items": [],
        }
        for item in self.items:
            result["items"].append(item.json)
        return result

    @property
    def words_json(self):
        return self._get_blocks_of_type("WORD")

    @property
    def lines_json(self):
        return self._get_blocks_of_type("LINE")

    def _get_blocks_of_type(self, type_="LINE"):
        return [block for block in self.data["Blocks"] if block["BlockType"] == type_]

    @staticmethod
    def get_bound_of_word(word, position: int = 1):
        return np.array((word["Geometry"]["Polygon"][position]["X"], word["Geometry"]["Polygon"][position]["Y"]))

    def r(self, point):
        """
        self.angle is measured like this: from horizontal line to what it is
        0,0               1,0
        +-------*-----------           ABC:             )8V
        |       *                     a=0.0             a=pi
        alpha  **      A
        |    **        | u             U                 >
        |  <*          | oo            oo   a=-pi/2     oo  a=pi/2
        |              | <             <                 A
        +-----------------1,1
        so in order to rotate from actual image (noted above) to normalized x/y,
        rotate with -self.angle around (0.5, 0.5)
        (that actually means just take angle and go counterclockwise on image)

        So, image -> normalized with angle= -pi/2 = -1.57
             0,0  -> 1,0
             1,0  -> 1,1
             1,1  -> 0,1
             0,1  -> 0,0
        """
        return rotate_point(-self.angle, point)

    def __repr__(self):
        return self.name
