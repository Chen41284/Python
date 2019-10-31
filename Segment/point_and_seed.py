# -*- coding: utf-8 -*-
import numpy as np


class Seed(object):

    def __init__(self, point, lower, upper, index):
        self.seed_zyx = point
        self.lower = lower
        self.upper = upper
        self.index = index


class Point(object):

    def __init__(self, z, y, x):
        self.z = z
        self.y = y
        self.x = x

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getZ(self):
        return self.z


class roberts_operator(object):
    def __init__(self):
        # x方向Roberts算子
        self.operator_x = np.array([[[1, 0], [0, -1]],
                                    [[0, 1], [-1, 0]]])
        # y方向Roberts算子
        self.operator_y = np.array([[[0, 1], [-1, 0]],
                                    [[1, 0], [0, -1]]])
        # z方向Roberts算子
        self.operator_z = np.array([[[0, -1], [1, 0]],
                                    [[1, 0], [0, -1]]])


