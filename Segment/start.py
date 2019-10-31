# -*- coding: utf-8 -*-

import numpy as np  #第三方库
from scipy.signal import argrelextrema  #第三方库
import random   #Python内建模块
import preprocess  # 自建
import point_and_seed as ps  #自建
import seg_entropy as seg  #自建
import volumerendering
import edge_detection as edge #自建
import SimpleITK as sitk


# 统计小波变化后的图像直方图
def wavelet_hist(image_data):
    [z, y, x] = image_data.shape
    # 创建直方图统计字典
    d = dict()
    for d_i in range(256):
        d[d_i] = list()
    for k in range(z):
        for j in range(y):
            for i in range(x):
                if image_data[k, j, i] != 0:
                # if 100 < image_data[k, j, i] < 256:
                    tmp = np.floor(image_data[k, j, i] + 0.5)
                    d[tmp].append([k, j, i])
    return d


# 提取种子点
def seed_extract(dic):
    seed_list = list()
    count_array = np.zeros(256)

    for i in range(256):
        count_array[i] = len(dic[i])

    # 直方图局部最小值所处的像素值
    less_extrema = np.array([])
    less_extrema = np.append(less_extrema, np.array(argrelextrema(count_array[0:140], np.less, order=6)))
    less_extrema = np.append(less_extrema, np.array(argrelextrema(count_array[140:180], np.less, order=4)) + 140)
    less_extrema = np.append(less_extrema, np.array(argrelextrema(count_array[180:], np.less, order=6)) + 180)
    # 直方图局部最大值所处的像素值
    greater_extrema = np.array([])  #[  5.  33.  90. 118. 135. 142. 148. 155. 163. 174. 182. 191. 203.]
    greater_extrema = np.append(greater_extrema, np.array(argrelextrema(count_array[0:140], np.greater, order=5)))
    # greater_extrema = np.append(greater_extrema, np.array(argrelextrema(count_array[70:140], np.greater, order=3)) + 70)
    greater_extrema = np.append(greater_extrema, np.array(argrelextrema(count_array[140:], np.greater, order=3)) + 140)

  
    index = 0
    last_seed_lower = 0
    for j in range(greater_extrema.size):
        for i in range(less_extrema.size-1):
            if greater_extrema[j] < less_extrema[i]:
                break
            if less_extrema[i] < greater_extrema[j] < less_extrema[i+1]:
                index += 1
                seed_total = np.array(dic[greater_extrema[j]])
                seed_zyx = np.array(random.sample(list(seed_total), 3))  #随机选取3个种子点
                if len(seed_list) == 0:
                    seed_list.append(ps.Seed(seed_zyx, less_extrema[i], less_extrema[i+1], index))
                    last_seed_lower = less_extrema[i]
                elif last_seed_lower != less_extrema[i]:
                    seed_list.append(ps.Seed(seed_zyx, less_extrema[i], less_extrema[i+1], index))
                    last_seed_lower = less_extrema[i]
                continue

    return seed_list


def start(file_dir, file_growing, file_edge):
    # print(file_dir)
    read = preprocess.read_dcm2array(file_dir)
    image_cw = preprocess.cw(read)
    coeffs = preprocess.wavelet3(image_cw)
    image_reduce = preprocess.wavelet_cw(coeffs[0])

    image_edge = edge.edge_detection(coeffs[0])
    volumerendering.show_edge(image_edge, file_edge)
   
    d = wavelet_hist(image_reduce)
    # # d = hist(image_cw)
    volume = []
    seed_tmp = seed_extract(d)
    grow_mark_all = np.zeros(image_reduce.shape)
    for i in range(len(seed_tmp)):
        seed_list_tmp = seed_tmp[i]
        # print seed_list_tmp.seed_zyx, seed_list_tmp.lower, seed_list_tmp.upper
        image_grow = seg.growing(image_reduce, seed_list_tmp,grow_mark_all)
        volume .append(volumerendering.show_growing(image_grow,i, file_growing))
    return volume


#程序的起点，不要界面的话
if __name__ == '__main__':
    file_dir = "./head/"
    file_growing = "./JPEG_Growing/"
    file_edge = "./JPEG_Edge/"
    start(file_dir, file_growing, file_edge)