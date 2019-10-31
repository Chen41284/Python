# -*- coding: utf-8 -*-

import numpy as np
import SimpleITK as sitk
import pywt
import edge_detection
import time


def read_dcm2array(path_dcm):
    if path_dcm is None:
        #path_dcm = r'C:\Users\chenjiaxing\Desktop\Practice\CPython\SimpleITK\head'
        print('Error not correct path')
        return
    reader = sitk.ImageSeriesReader()
    #print('reader')
    filenames = reader.GetGDCMSeriesFileNames(path_dcm)
    #print('filenames')
    reader.SetFileNames(filenames)
    #print('SetFileNames')
    img_original = reader.Execute()
    #print('Execute')
    image = sitk.GetArrayFromImage(img_original)  # Z,Y,X
    image_array = np.array(image)
    return image_array


def cw(image_data):
    # CT图像数据重新调整，转换为HU值
    fRescaleSlope = 1.0
    fRescaleIntercept = -1024
    #imageU = image_data * fRescaleSlope + fRescaleIntercept  #数组中的每个元素乘以fRescaleSlop，然后加上fRescaleIntercept

    # 图像调窗
    width = 985.0  # 窗宽
    level = -679.0  # 窗位
    imageCW = image_data
    im_shape = image_data.shape
    lenZ = im_shape[0]
    lenY = im_shape[1]
    lenX = im_shape[2]
    for k in range(lenZ): #不包括lenZ
        for i in range(lenY):
            for j in range(lenX):
                temp = imageCW[k, i, j]
                imageCW[k, i, j] = imageCW[k, i, j] * fRescaleSlope + fRescaleIntercept
                if imageCW[k, i, j] < level - width / 2.0:
                    imageCW[k, i, j] = 0.0
                else:
                    if imageCW[k, i, j] > level + width / 2.0:
                        imageCW[k, i, j] = 255.0
                    else:
                        imageCW[k, i, j] = (temp + width / 2.0 - level) * 255.0 / width
    return imageCW


# 三维小波变化
def wavelet3(image_data):
    # coeffs = [aaa, (aad, ada, daa, add, dad, dda, ddd), (aad2, ada2, daa2, add2, dad2, dda2, ddd2)]
    coeffs = pywt.wavedecn(image_data, 'db1', level=2)
    return coeffs


# 小波后进行数据调整  将灰度值归一化到0~255
def wavelet_cw(image_data):
    [z, y, x] = image_data.shape
    for k in range(z):
        min = np.amin(image_data[k, :, :])    #取x，y中的最小值
        max = np.amax(image_data[k, :, :])    #取x，y中的最大值
        for i in range(y):
            for j in range(x):
                image_data[k, i, j] = (image_data[k, i, j] - min) * 255.0 / (max - min)
    return image_data

# 平均值采样减少图像数据
def image_reduce_dim(image_data):
    [z, y, x] = image_data.shape
    img_reduce = np.zeros([z, y/4, x/4])
    for h in range(y/4):
        for w in range(x/4):
            j = h * 4
            i = w * 4
            #取出所有z的i,j进行计算，计算的结果是一维数组 
            tmp = (image_data[:, j, i] + image_data[:, j + 1, i] + image_data[:, j, i + 1] + image_data[:, j + 1, i + 1]) / 4.0 
            img_reduce[:, h, w] = tmp
    return img_reduce
    


