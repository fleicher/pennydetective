import math
from unittest import TestCase
from util import get_abs_perp_angle_diff, get_dist_to_line, rotate_point


class TestUtil(TestCase):

    def test_get_abs_perp_angle_diff(self):
        values = [
            (0, 0, math.pi/2),
            (0, math.pi/2, 0),
            (-math.pi/4, math.pi/4, 0),
            (0.030444919373909873, 1.7865575985447855, 1.7865575985447855-0.030444919373909873-math.pi/2)
        ]
        for a1, a2, r in values:
            angle_diff = get_abs_perp_angle_diff(a1, a2)
            self.assertAlmostEqual(angle_diff, r)

    def test_rotate_point(self):
        values = [
            (0,          (1, 0), (1, 0)),
            (math.pi/2,  (1, 0), (1, 1)),
            (-math.pi,   (1, 0), (0, 1)),
            (-math.pi/2, (1, 0), (0, 0))
        ]
        for angle, point, expected in values:
            calculated = rotate_point(angle, point)
            self.assertAlmostEqual(calculated[0], expected[0])
            self.assertAlmostEqual(calculated[1], expected[1])

    def test_get_dist_to_line(self):
        values = [
            ((0, 0), (0, 1), (1, 1), 1)
        ]
        for l1, l2, p, expected in values:
            calculated = get_dist_to_line(l1, l2, p)
            self.assertAlmostEqual(calculated, expected)
