import math
import re

import numpy as np
from numpy.linalg import norm


def rotate_point(angle, point, pivot=(.5, .5)):
    """
    :param angle: angle in radius
    :param point: rotate this point
    :param pivot: rotate other point around this one
    :return:

    Rotate a point counterclockwise by a given angle around a given origin.
    As for images the y-axis is counted top to bottom, for such images
    the rotation can be taken to be clockwise.
    """
    ox, oy = pivot
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def get_angle(point1, point2):
    """
    :return: the angle of the line that runs from point1 to point2
    """
    return math.atan2(point2[1] - point1[1], point2[0] - point1[0])


def get_abs_perp_angle_diff(angle1, angle2):
    """
    :param angle1:
    :param angle2:
    :return: the absolute inner angle difference between two lines that cross
    each other in the origin and have angle1 and angle2
    """
    angle_diff = (abs(angle2 - angle1 + math.pi/2)) % math.pi
    result = min(math.pi - angle_diff, angle_diff)
    assert 0 <= result <= math.pi/2
    return result


def get_dist_to_line(line_point1, line_point2, point):
    """
    :param line_point1: first point defining the line
    :param line_point2: second point defining the line
    :param point: the to calculate the distance to
    :return: distance between point and the defined line
    """
    line_point1 = np.array(line_point1)
    line_point2 = np.array(line_point2)
    point = np.array(point)
    return norm(np.cross(line_point2 - line_point1, line_point1 - point)) / norm(line_point2 - line_point1)


def distance_between_two_points(a, b):
    """https://stackoverflow.com/questions/1401712/how-can-the-euclidean-distance-be-calculated-with-numpy"""
    return np.linalg.norm(a - b)


def format_price(price):
    """ remove all non number characters and take care of ',' -> '.' conversion"""
    return float(re.sub('[^0-9.]+', '', price.replace(",", ".")))
