from itertools import count
from pickle import NONE
import cv2
import numpy as np
import os
import shutil
from scipy.spatial.kdtree import distance_matrix
from sklearn.neighbors import NearestNeighbors
from scipy import spatial
import re
import copy
from sklearn.cluster import KMeans
from sklearn import cluster
import json
import datetime
import math
from decimal import getcontext, Decimal
# import cupy as cp
import concurrent.futures

class CircleDetect():
    def __init__(self, inputDirectory : str, outputDirectory: str) -> None:
        self.InputDir = inputDirectory
        self.OutputDir = outputDirectory
        self.ImageSpacing = 0.3
        self.DetectMatrix = []
        self.CircleMatrix = None
        self.CircleDiameter = 2.5
        self.factor_distance = 1.5
        self.CircleNum = 7
        self.MarkerPoints = None
        self.sortThreshold = 2
        self.UpdateThreshold = 6
        self.ImageOrigin = [0, 0, 0]
        self.X_middle = 0
        self.Accuracy = 0.50
        self.denoising = False

        self.centerDistance = 12.7    # marker上各个点到质心点的平均距离
        self.maxdeviation = 0.0
        self.averagedeviation = 0.0
        self.distance_list = [96.14, 104.39, 105.73, 113.68, 117.48 , 122.87, 123.87]

        # 全局的Image图像
        self.Image_Axial = None
        self.Image_Sagittal = None
        self.Image_Coronal = None
        self.direction = None
        self.Image = None

    def setImageSpacing(self, value):
        self.ImageSpacing = value
    
    def setdenoising(self, value):
        self.denoising = value

    # def setImageAxial(self, image):
    #     self.Image_Axial = cp.asnumpy(image)

    # def setImageSagittal(self, image):
    #     self.Image_Sagittal = cp.asnumpy(image)

    # def setImageCoronal(self, image):
    #     self.Image_Coronal = cp.asnumpy(image)
    
    def setAccuracy(self, value):
        self.Accuracy = value

    def setImageOrigin(self, value):
        self.ImageOrigin = value
    
    def setUpdateThreshold(self, value):
        self.UpdateThreshold = value
    
    def setsortThreshold(self, value):
        self.sortThreshold = value
    
    def setCircleDiameter(self, value):
        self.CircleDiameter = value
    
    def setDistanceFactor(self, value):
        self.factor_distance = value
    
    def getmaxdeviation(self):
        return self.maxdeviation
    
    def getaveragedeviation(self):
        return self.averagedeviation
            
    def createDir(self, TEMP_PATH):
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, True)
            os.makedirs(TEMP_PATH)
        else:
            os.makedirs(TEMP_PATH)
        return True
    
    def setCircleNum(self, value):
        self.CircleNum = value
    
    def computeDeviation(self, data):
        estimator = KMeans(n_clusters=1)
        estimator.fit_predict(data)
        centroids = estimator.cluster_centers_
        center_point = centroids[0]
        sum_distance = 0
        for y in data:
            dist = np.linalg.norm(y - center_point)
            sum_distance = sum_distance + dist
        
        average_distance = sum_distance / len(data)

        # self.deviation = abs(average_distance - self.centerDistance) / self.centerDistance
        self.deviation = abs(average_distance - self.centerDistance)

        dist_mat = spatial.distance_matrix(data, data)
        temp = np.sum(dist_mat, axis=0)
        print("------------------------------------------------")
        print("total distance ", np.sum(temp))
        index = np.argsort(temp)
        print(temp[index])
        dist_np = np.array(self.distance_list, dtype = np.float)
        dist_error = np.abs(dist_np - temp[index]) / (self.CircleNum - 1)
        self.maxdeviation = np.max(dist_error)
        self.averagedeviation = np.average(dist_error)
        print("dist_error ", dist_error)
        print("maxdeviation ", self.maxdeviation)
        print("averagedeviation ", self.averagedeviation)
        print("------------------------------------------------")

    
    def filter_marker(self, data):
        estimator = KMeans(n_clusters=1)
        estimator.fit_predict(data)
        centroids = estimator.cluster_centers_
        center_point = centroids[0]
        distance = []
        distance_Z = []
        for y in data:
            dist = np.linalg.norm(y - center_point)
            distance.append(dist)
            distance_Z.append(abs(y[2] - center_point[2]))
        
        outliers = []
        marker_point = []
        mean_distance = np.mean(distance)
        mean_distance_Z = np.mean(distance_Z)

        distance_Z = []  # 清空列表
        for y in data:
            dist = np.linalg.norm(y - center_point)
            # if ((dist > mean_distance * self.factor_distance) 
            # or ((abs(y[2] - center_point[2]) > mean_distance_Z * self.factor_distance))):
            if ((dist > mean_distance * self.factor_distance)):
                outliers.append(y)
            else:
                marker_point.append(y)
                # distance_Z.append(abs(y[2] - center_point[2]))
                distance_Z.append(y[2])
        
        outliers = np.array(outliers, dtype = np.float32)
        marker_point = np.array(marker_point, dtype = np.float32)

        # 按Z轴的坐标数值进行排序，因为Marker下方有胶水
        distance_Z = np.array(distance_Z, dtype = np.float32)
        dist_sort = np.argsort(-distance_Z)

        length = min(len(marker_point), self.CircleNum)

        temp = np.array(marker_point[dist_sort], dtype = np.float)
        print('\033[92m =================filter marker_point=========================')
        np.set_printoptions(formatter={'float': '{: 0.3f}'.format})
        print(temp)
        print('\033[92m ==========================================')       

        return marker_point[dist_sort[0:length]]
    
    def cirlce_matrix(self, dir : str, direction = "Axial", minR=0, maxR=20):
        Radius = self.CircleDiameter / self.ImageSpacing / 2

        Area = math.pi * Radius * Radius
        arcLength = 2 * math.pi * Radius

        print("Radius ", Radius)
        print("Area ", Area)

        filelist = os.listdir(dir)  # 列出文件夹下所有的目录与文件
        valid = len(filelist) > 0
        if not valid:
            return
        
        for i in range(0, len(filelist)):
            filePath = os.path.join(dir, filelist[i])
            image = cv2.imread(filePath)
            regex = re.compile(r'\d+')
            # dst = cv2.GaussianBlur(image,(13,15),15)     #使用高斯模糊，修改卷积核ksize也可以检测出来
            # img_median = cv2.medianBlur(image, 5)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret,thresh = cv2.threshold(gray,127,255,0)   # 需要进行二值化，否则检测出来的轮廓会比较大
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            dst = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            dst2 = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, kernel)
            # circles = cv2.HoughCircles(dst, cv2.HOUGH_GRADIENT,1,20,param1=100,param2=8, minRadius=minR, maxRadius=maxR)

            contours = None
            if self.denoising:
                contours, hierarchy = cv2.findContours(dst2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            else:
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            valid = len(contours) > 0
            if not valid:
                continue
            # num = len(contours)
            if direction == "Axial" : # 横断面的检测:
                Z_index = int(max(regex.findall(filelist[i])))

                try:
                    # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                    templist = []
                    templist.clear()
                    for k in range(len(contours)):
                        rect = cv2.minAreaRect(contours[k])
                        center, size = rect[0], rect[1]
                        RectArea = cv2.contourArea(contours[k])
                        arc = cv2.arcLength(contours[k], True)

                        if (len(self.DetectMatrix) == 0):
                            cir = [center[0], center[1], Z_index, RectArea, 1]
                            self.DetectMatrix.append(cir)
                            continue   

                        # 面积可以设置得小一些，以便将种植体过滤掉
                        # if (size[0] < 8 or size[0] > 20 or size[1] < 8 or size[1] > 20):
                        #     continue

                        if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                            continue

                        if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                            continue

                        add_Item = True
                        R = Radius * 1.0
                        self.X_middle = image.shape[0] / 2
                        
                        for c in self.DetectMatrix:
                            # 新增判断是否连续的序列
                            Z_pre = int(c[2] / c[4]) + int(c[4] / 2)
                            if ( (abs(c[0] - center[0]) < R) and (abs(c[1] - center[1]) < R) and (abs(Z_index - Z_pre) == 1)):   # 可能是同一个圆
                            # if ( (abs(c[0] - center[0]) < R) and (abs(c[1] - center[1]) < R)):   # 可能是同一个圆
                                c[4] = c[4] + 1
                        #         # c[2] = (c[2] + Z_index) / 2  # 容易导致偏大
                                c[2] = c[2] + Z_index

                                if (RectArea > c[3]):
                                    c[3] = RectArea
                                    c[0] = center[0]
                                    c[1] = center[1]
                                add_Item = False   
                                
                        if add_Item:
                            cir = [center[0], center[1], Z_index, RectArea, 1]
                            templist.append(cir)

                    for t in templist:
                        self.DetectMatrix.append(copy.deepcopy( t ))    # 深拷贝
                except:
                    print("Axial error, Z_index ", Z_index)
            elif direction == "Sagittal" :    # 矢状面
                X_index = int(max(regex.findall(filelist[i])))
                try:
                    # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                    templist = []
                    for k in range(len(contours)):
                        rect = cv2.minAreaRect(contours[k])
                        center, size = rect[0], rect[1]
                        RectArea = cv2.contourArea(contours[k])
                        arc = cv2.arcLength(contours[k], True)
                        Z_value = image.shape[0] - center[1]

                        # if (size[0] < 8 or size[0] > 19 or size[1] < 8 or size[1] > 19):
                        #     continue

                        if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                            continue

                        if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                            continue

                        add_Item = True
                        R = Radius * 0.5
                        for c in self.DetectMatrix:
                            # 把X_index也计入，进行一个三维空间的同时判断
                            X_value = X_index * self.ImageSpacing
                            if ( (abs(c[2] - Z_value) < R) and (abs(c[1] - center[0]) < R)):   # 可能是同一个圆
                                c[4] = c[4] + 1

                                if (RectArea > c[3]):
                                    c[3] = RectArea
                                    c[1] = center[0]

                                add_Item = False

                        if add_Item:
                            cir = [X_index, center[0], Z_value, RectArea, 1]
                            templist.append(cir)
                    
                    for t in templist:
                        self.DetectMatrix.append(copy.deepcopy( t ))
                except:
                    print("Sagittal error, X_index ", X_index)
            elif direction == "Coronal" :    # 矢状面
                Y_index = int(max(regex.findall(filelist[i])))
                try:
                    # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                    templist = []
                    for k in range(len(contours)):
                        rect = cv2.minAreaRect(contours[k])
                        center, size = rect[0], rect[1]
                        RectArea = cv2.contourArea(contours[k])
                        arc = cv2.arcLength(contours[k], True)
                        Z_value = image.shape[0] - center[1]

                        # if (size[0] < 8 or size[0] > 19 or size[1] < 8 or size[1] > 19):
                        #     continue

                        if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                            continue

                        if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                            continue

                        add_Item = True
                        R = Radius * 0.5
                        for c in self.DetectMatrix:
                            # 把Y_index也计入，进行一个三维空间的同时判断
                            # Y_value = Y_index * self.ImageSpacing
                            if ( (abs(c[2] - Z_value) < R) and (abs(c[0] - center[0]) < R) ):   # 可能是同一个圆
                                c[4] = c[4] + 1

                                if (RectArea > c[3]):
                                    c[3] = RectArea
                                    c[0] = center[0]

                                add_Item = False

                        if add_Item:
                            cir = [center[0], Y_index, Z_value, RectArea, 1]
                            templist.append(cir)
                    
                    for t in templist:
                        self.DetectMatrix.append(copy.deepcopy( t ))
                except:
                    print("Sagittal error, X_index ", X_index)
            else:
                return
        
        # 以横断面的检测为主，矢状面和横断面为辅（主要提高圆心的更新数）
        if direction == "Axial":
            self.DetectMatrix = np.array(self.DetectMatrix, dtype = np.float)
            self.DetectMatrix[:, 2] = self.DetectMatrix[:, 2] / self.DetectMatrix[:, 4]

            # self.DetectMatrix[:, 0] = self.DetectMatrix[:, 0] / self.DetectMatrix[:, 4]
            # self.DetectMatrix[:, 1] = self.DetectMatrix[:, 1] / self.DetectMatrix[:, 4]

            self.DetectMatrix = self.DetectMatrix.tolist()


    
    def cirlce_matrix_Image(self, index):
        Radius = self.CircleDiameter / self.ImageSpacing / 2

        Area = math.pi * Radius * Radius
        arcLength = 2 * math.pi * Radius

        gray = self.image[:, :, index]
        _,thresh = cv2.threshold(gray,127,255,0)   # 需要进行二值化，否则检测出来的轮廓会比较大
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dst = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        dst2 = cv2.morphologyEx(dst, cv2.MORPH_CLOSE, kernel)
        # circles = cv2.HoughCircles(dst, cv2.HOUGH_GRADIENT,1,20,param1=100,param2=8, minRadius=minR, maxRadius=maxR)

        contours = None
        if self.denoising:
            contours, _ = cv2.findContours(dst2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        else:
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        valid = len(contours) > 0
        if not valid:
            return
        # num = len(contours)
        if self.direction == "Axial" : # 横断面的检测:
            Z_index = index

            try:
                # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                templist = []
                templist.clear()
                for k in range(len(contours)):
                    rect = cv2.minAreaRect(contours[k])
                    center, size = rect[0], rect[1]
                    RectArea = cv2.contourArea(contours[k])
                    arc = cv2.arcLength(contours[k], True)

                    if (len(self.DetectMatrix) == 0):
                        cir = [center[0], center[1], Z_index, RectArea, 1]
                        self.DetectMatrix.append(cir)
                        continue   

                    # 面积可以设置得小一些，以便将种植体过滤掉
                    # if (size[0] < 8 or size[0] > 20 or size[1] < 8 or size[1] > 20):
                    #     continue

                    if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                        continue

                    if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                        continue

                    add_Item = True
                    R = Radius * 1.0
                    self.X_middle = self.image.shape[0] / 2
                    
                    for c in self.DetectMatrix:
                        # 新增判断是否连续的序列
                        Z_pre = int(c[2] / c[4]) + int(c[4] / 2)
                        if ( (abs(c[0] - center[0]) < R) and (abs(c[1] - center[1]) < R) and (abs(Z_index - Z_pre) == 1)):   # 可能是同一个圆
                        # if ( (abs(c[0] - center[0]) < R) and (abs(c[1] - center[1]) < R)):   # 可能是同一个圆
                            c[4] = c[4] + 1
                    #         # c[2] = (c[2] + Z_index) / 2  # 容易导致偏大
                            c[2] = c[2] + Z_index

                            if (RectArea > c[3]):
                                c[3] = RectArea
                                c[0] = center[0]
                                c[1] = center[1]
                            add_Item = False   
                            
                    if add_Item:
                        cir = [center[0], center[1], Z_index, RectArea, 1]
                        templist.append(cir)

                for t in templist:
                    self.DetectMatrix.append(copy.deepcopy( t ))    # 深拷贝
            except:
                print("Axial error, Z_index ", Z_index)
        elif self.direction == "Sagittal" :    # 矢状面
            X_index = index
            try:
                # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                templist = []
                for k in range(len(contours)):
                    rect = cv2.minAreaRect(contours[k])
                    center, size = rect[0], rect[1]
                    RectArea = cv2.contourArea(contours[k])
                    arc = cv2.arcLength(contours[k], True)
                    Z_value = self.image.shape[0] - center[1]

                    # if (size[0] < 8 or size[0] > 19 or size[1] < 8 or size[1] > 19):
                    #     continue

                    if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                        continue

                    if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                        continue

                    add_Item = True
                    R = Radius * 0.50
                    for c in self.DetectMatrix:
                        # 把X_index也计入，进行一个三维空间的同时判断
                        X_value = X_index * self.ImageSpacing
                        if ( (abs(c[2] - Z_value) < R) and (abs(c[1] - center[0]) < R)):   # 可能是同一个圆
                            c[4] = c[4] + 1

                            if (RectArea > c[3]):
                                c[3] = RectArea
                                c[1] = center[0]

                            add_Item = False

                    if add_Item:
                        cir = [X_index, center[0], Z_value, RectArea, 1]
                        templist.append(cir)
                
                for t in templist:
                    self.DetectMatrix.append(copy.deepcopy( t ))
            except:
                print("Sagittal error, X_index ", X_index)
        elif self.direction == "Coronal" :    # 矢状面
            Y_index = index
            try:
                # circles = np.float32(np.around(circles)) #around对数据四舍五入，为整数
                templist = []
                for k in range(len(contours)):
                    rect = cv2.minAreaRect(contours[k])
                    center, size = rect[0], rect[1]
                    RectArea = cv2.contourArea(contours[k])
                    arc = cv2.arcLength(contours[k], True)
                    Z_value = self.image.shape[0] - center[1]

                    # if (size[0] < 8 or size[0] > 19 or size[1] < 8 or size[1] > 19):
                    #     continue

                    if ((RectArea < Area * self.Accuracy ) or (RectArea > Area * (2 - self.Accuracy))):
                        continue

                    if ((arc < arcLength * self.Accuracy ) or (arc > arcLength * (2 - self.Accuracy))):
                        continue

                    add_Item = True
                    R = Radius * 0.5
                    for c in self.DetectMatrix:
                        # 把Y_index也计入，进行一个三维空间的同时判断
                        # Y_value = Y_index * self.ImageSpacing
                        if ( (abs(c[2] - Z_value) < R) and (abs(c[0] - center[0]) < R) ):   # 可能是同一个圆
                            c[4] = c[4] + 1

                            if (RectArea > c[3]):
                                c[3] = RectArea
                                c[0] = center[0]

                            add_Item = False

                    if add_Item:
                        cir = [center[0], Y_index, Z_value, RectArea, 1]
                        templist.append(cir)
                
                for t in templist:
                    self.DetectMatrix.append(copy.deepcopy( t ))
            except:
                print("Sagittal error, X_index ", X_index)
        else:
            return
        
        # 以横断面的检测为主，矢状面和横断面为辅（主要提高圆心的更新数）
        if self.direction == "Axial":
            self.DetectMatrix = np.array(self.DetectMatrix, dtype = np.float)
            self.DetectMatrix[:, 2] = self.DetectMatrix[:, 2] / self.DetectMatrix[:, 4]

            # self.DetectMatrix[:, 0] = self.DetectMatrix[:, 0] / self.DetectMatrix[:, 4]
            # self.DetectMatrix[:, 1] = self.DetectMatrix[:, 1] / self.DetectMatrix[:, 4]

            self.DetectMatrix = self.DetectMatrix.tolist()    
    def detect_circle(self, minR=0, maxR=20):
        circle_input_Axial = self.InputDir + "/Axial"
        self.cirlce_matrix(circle_input_Axial, "Axial", minR, maxR)

        circle_input_Sagittal = self.InputDir + "/Sagittal"
        self.cirlce_matrix(circle_input_Sagittal, "Sagittal", minR, maxR)

        circle_input_Coronal = self.InputDir + "/Coronal"
        self.cirlce_matrix(circle_input_Coronal, "Coronal", minR, maxR)


        # 不适合使用并行计算，计算的误差会增大
        # self.direction = "Axial"
        # index = list(range(0, self.Image_Axial.shape[2], 1))
        # self.image = self.Image_Axial
        # with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
        #     executor.map(self.cirlce_matrix_Image, index)

        # self.direction = "Sagittal"
        # self.image = self.Image_Sagittal
        # index = list(range(0, self.Image_Sagittal.shape[2], 1))
        # with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
        #     executor.map(self.cirlce_matrix_Image, index)

        # self.direction = "Coronal"
        # self.image = self.Image_Coronal
        # index = list(range(0, self.Image_Coronal.shape[2], 1))
        # with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
        #     executor.map(self.cirlce_matrix_Image, index)



        # 过溜掉种植体和探针验证点, 种植体和验证点均在对侧

        Matrix = np.array(self.DetectMatrix, dtype = np.int32) 
        # print(Matrix)
        index = np.argsort(-Matrix[:, 4])

        tempSum = np.sum(Matrix[index[0:10], :], axis=0)
        X_average = tempSum[0] / 10

        print("tempSum[0] ", tempSum[0])
        print("len(tempSum) ", len(self.DetectMatrix))
        print("X_average ", X_average)
        print("self.X_middle", self.X_middle)

        if (X_average > self.X_middle):
            for k in range(len(self.DetectMatrix)-1, -1, -1):
                if (self.DetectMatrix[k][0] < self.X_middle):
                    self.DetectMatrix.pop(k)
        else:
            for k in range(len(self.DetectMatrix)-1, -1, -1):
                if (self.DetectMatrix[k][0] > self.X_middle):
                    self.DetectMatrix.pop(k)
        #################################################################            

        self.DetectMatrix = np.array(self.DetectMatrix, dtype = np.int32) 

        detectMatrix = self.DetectMatrix
        X_sort = np.argsort(detectMatrix[:, 0])

        index = np.argsort(-detectMatrix[:, 4])
        print("===========================================================")
        print("detectMatrix \n", detectMatrix[index][0:20, :])
        print("===========================================================")
        self.CircleMatrix = detectMatrix[index][0:(self.CircleNum), :]  # 暂时不考虑种植体的情况
        # self.CircleMatrix = detectMatrix[index]

        # self.UpdateThreshold = min(detectMatrix[index[0] , 4] * 0.5, detectMatrix[index[self.CircleNum] , 4] )
        # print("self.UpdateThreshold ", self.UpdateThreshold)
        # self.UpdateThreshold = 10
        # self.CircleMatrix = self.CircleMatrix[self.CircleMatrix[:, 4] >= self.UpdateThreshold,:]  # 根据更新次数进行过滤

        print("self.CircleMatrix \n", self.CircleMatrix)

        circlePosition = self.CircleMatrix * self.ImageSpacing
        circlePosition = circlePosition[:, 0:3]

        print("*******************************************")
        # test = circlePosition.tolist()
        # print("test ", test)
        print("*******************************************")

        print("self.circleNum " , self.CircleNum)

        markerPoints = circlePosition
        # if (len(circlePosition) > self.CircleNum):
        #     markerPoints = self.filter_marker(circlePosition)  # 过滤掉偏差比较大的点, 距离过滤
        # else:
        #     markerPoints = circlePosition                      # 满足条件的球的数量已经不够，则不进行过滤
        print("===========================================================")
        print(markerPoints)
        print("===============after sort==================================")
        markerPoints = self.bubbleSort(markerPoints)
        
        if self.CircleNum == 7:
            self.computeDeviation(markerPoints)

        print("===========================================================")
        print("origin ", self.ImageOrigin)
        Origin = np.array(self.ImageOrigin)
        markerPoints = markerPoints + Origin
        self.MarkerPoints = markerPoints
        print(markerPoints)
        print("maxdeviation error ", self.maxdeviation)
        print("averagedeviation error ", self.averagedeviation)
        print("===========================================================")

        return markerPoints
    
    def bubbleSort(self, arr):
        '''
        对检测出来的球新进行排序，按X数值由小到大进行排序
        比较X的数值的时候，如果X轴之间的数值差值小于1，则比较Y轴的数值，也是由小到大进行排序
        '''
        n = len(arr)
        # 遍历所有数组元素
        for i in range(n):   
            # Last i elements are already in place
            for j in range(0, n-i-1):

                first = (abs(arr[j][0] - arr[j + 1][0]) > self.sortThreshold) and (arr[j][0] > arr[j + 1][0])
                second = (abs(arr[j][0] - arr[j + 1][0]) < self.sortThreshold) and (arr[j][1] > arr[j + 1][1])
                if (first or second):
                    arr[j], arr[j + 1] = copy.deepcopy(arr[j + 1]), copy.deepcopy(arr[j])
        
        return arr
    
    def UpdateJson(self, filename, OperativeStage = 'postoperative'):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                info_dict = json.load(f)
                # n = len(self.MarkerPoints)
                n = self.CircleNum
                for i in range(n):
                    info_dict[OperativeStage]['MarkerPoints'][str(i + 1)]['x'] = str(self.MarkerPoints[i][0])
                    info_dict[OperativeStage]['MarkerPoints'][str(i + 1)]['y'] = str(self.MarkerPoints[i][1])
                    info_dict[OperativeStage]['MarkerPoints'][str(i + 1)]['z'] = str(self.MarkerPoints[i][2])
                info_dict[OperativeStage]['maxError'] = str(Decimal(self.maxdeviation).quantize(Decimal('0.00')))
                info_dict[OperativeStage]['averageError'] = str(Decimal(self.averagedeviation).quantize(Decimal('0.00')))
            except:
                print("circleDetec cannot read or update json file")

        ## 将info_dict写入app.json文件
        with open(filename, 'w', encoding='utf-8') as f1:
            f1.write(json.dumps(info_dict, indent=4, ensure_ascii=False))
    
if __name__ == '__main__':

    # inputDirectory = "C:/Users/Admin/Desktop/Code/Python/TargetDetect/Axial"
    # outputDirectory = "C:/Users/Admin/Desktop/Code/Python/TargetDetect/Classification"

    inputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect"
    outputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect/Classification"

    circle = CircleDetect(inputDirectory, None)
    circle.setUpdateThreshold(6)
    circle.detect_circle()
    circle.setCircleDiameter(2.5)
    circle.setDistanceFactor(1.5)
    circle.setsortThreshold(3)
    circle.UpdateJson('operativedata.json')

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()