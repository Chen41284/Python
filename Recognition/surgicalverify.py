import os
from pickle import FALSE
from sre_constants import MIN_REPEAT

from sympy import false
import DicomToPNG, ImplantDetect, CornerDetect, CircleDetect
import json
import numpy as np
import copy
import datetime
from xml.dom.minidom import parse
import xml.dom.minidom
import pandas as pd
import vtk
import math
from colorama import Fore, Back, Style
import itertools
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors
from scipy import spatial

class SurgicalVerify():
    def __init__(self, inputDirectory : str, outputDirectory: str) -> None:
        self.InputDir = inputDirectory
        self.OutputDir = outputDirectory
        self.ImageSpacing = 0.226
        self.preoperative = np.ones([7,3], dtype = float)
        self.postoperative = np.ones([7,3], dtype = float)
        self.pre_five = np.ones([5,3], dtype = float)
        self.post_five = np.ones([5,3], dtype = float)
        self.sortThreshold = 1
        self.UpdateThreshold = 5
        self.window_center = 2700   # 2715
        self.window_width = 500   # 884
        self.ImplantArea = "46"
        self.JsonFile = ""
        self.ImplantLength = 12
        self.ImplantWidth = 4.1
        self.CircleDiameter = 2.5
        self.factor_distance = 2.0   # 1.5
        self.minDistance = 10
        self.qualityLevel = 0.01
        self.maxCorners = 200
        self.Accuracy = 0.90
        self.MpsFile = ""
        self.ImageOrigin = [0, 0, 0]
        self.CircleNum = 7
        self.ImplantPosition = np.ones([2,6], dtype = float)

        self.detect_Implant = True
        self.OperativeStage = "postoperative"

        self.maxtrix_pre2post = None
        self.implant_position = None
        self.root_position = None

        # 全局的Image图像
        self.Image_Axial = None
        self.Image_Sagittal = None
        self.Image_Coronal = None

        self.multiVerify = True
        self.solid = False
        self.pre_comb = None
        self.post_comb = None
        
    def setsolid(self, value):
        self.solid = value
  
    def setsortThreshold(self, value):
        self.sortThreshold = value

    def setMultiVerify(self, value):
        self.multiVerify = value

    def setUpdateThreshold(self, value):
        self.UpdateThreshold = value
    
    def setCircleNum(self, value):
        self.CircleNum = value
    
    def setOperativeStage(self, value : str):
        self.OperativeStage = value
    
    def setMpsFile(self, value):
        self.MpsFile = value
    
    def setdetectImplant(self, value):
        self.detect_Implant = value

    def setAccuracy(self, value):
        self.Accuracy = value

    def setImageSpacing(self, value):
        self.ImageSpacing = value 
    
    def setCircleDiameter(self, value):
        self.CircleDiameter = value
    
    def setJsonFile(self, value):
        self.JsonFile = value

    def setWindowCenter(self, value : int):
        self.window_center = value
    
    def setWindowWidth(self, value : int):
        self.window_width = value

    def setImplantWidth(self, value):
        self.ImplantWidth = value
    
    def setImplantLength(self, value):
        self.ImplantLength = value
    
    def setImplantArea(self, value):
        self.ImplantArea = value

    def setCircleDiameter(self, value):
        self.CircleDiameter = value
    
    def setDistanceFactor(self, value):
        self.factor_distance = value
    
    def setShiTomasiCornerParam(self, minDistance, qualityLevel, maxCorners):
        self.minDistance = minDistance
        self.qualityLevel = qualityLevel
        self.maxCorners = maxCorners
    
    def AutoDetect(self):
        starttime = datetime.datetime.now()
        dicom2png = DicomToPNG.DicomToPNG(self.InputDir, self.OutputDir)
        dicom2png.readImage()
        dicom2png.setWindowCenter(self.window_center)
        dicom2png.setWindowWidth(self.window_width)
        dicom2png.writePNGseries()
        imageSpacing = dicom2png.GetImageSpacing()
        print("Image Spacing", imageSpacing)
        # dicom2png.slice("Z")   # 横断面的图像
        # dicom2png.slice("X")   # 矢状面的图像
        endtime = datetime.datetime.now()
        self.Image_Axial = dicom2png.GetImageAxial()
        self.Image_Coronal = dicom2png.GetImageCoronal()
        self.Image_Sagittal = dicom2png.GetImageSagittal()
        print("writePNGseries Time: ", (endtime - starttime))

        origin = dicom2png.GetImageOrigin()
        print("====Image Oring======", origin)
        print("self.detect_Implant ", self.detect_Implant)

        # circle_input = self.OutputDir + "/Axial"
        starttime = datetime.datetime.now()       
        circle_input = self.OutputDir
        circle = CircleDetect.CircleDetect(circle_input, None)
        circle.setdenoising(False)
        circle.setImageOrigin(origin)
        circle.setCircleDiameter(self.CircleDiameter)
        circle.setDistanceFactor(self.factor_distance)
        circle.setsortThreshold(self.sortThreshold)
        circle.setUpdateThreshold(self.UpdateThreshold)
        print("start circleNum ", self.CircleNum)
        circle.setCircleNum(self.CircleNum)
        circle.setImageSpacing(imageSpacing[0])
        # circle.setImageAxial(self.Image_Axial)
        # circle.setImageCoronal(self.Image_Coronal)
        # circle.setImageSagittal(self.Image_Sagittal)
        circle.detect_circle()
        circle.UpdateJson(self.JsonFile, self.OperativeStage)

        self.ReadJson()
        verify.selectOptimalPoint()
        self.ImageOrigin = origin

        if self.detect_Implant:
            # detect_input = self.OutputDir + "/Sagittal"
            starttime = datetime.datetime.now()
            detect_input = self.OutputDir
            detect_output = self.OutputDir + "/Classification"
            detect = ImplantDetect.ImplantDetect(detect_input, detect_output)
            detect.setImplantArea(self.ImplantArea)
            detect.setImplantLength(self.ImplantLength)
            detect.setImplantWidth(self.ImplantWidth)
            detect.setImageSpacing(imageSpacing[0])
            detect.setMultiVerify(self.multiVerify)
            detect.setfilter_x((self.implant_position[0] + self.root_position[0]) / 2 - self.ImageOrigin[0])
            detect.setfilter_y((self.implant_position[1] + self.root_position[1]) / 2 - self.ImageOrigin[1])
            detect.setfilter_z((self.implant_position[2] + self.root_position[2]) / 2 - self.ImageOrigin[2])
            # detect.classify()
            # detect.SSIM_filter()
            detect.ImplantDetect()
            endtime = datetime.datetime.now()
            print("detect Implant Time: ", (endtime - starttime))

            starttime = datetime.datetime.now()
            corner_input = self.OutputDir + "/CornerDetect"
            corner = CornerDetect.CornerDetect(corner_input, None)
            corner.setImageOrigin(origin)
            corner.setImplantArea(self.ImplantArea)
            corner.setImageSpacing(imageSpacing[0])
            corner.setImplantLength(self.ImplantLength)
            corner.setImplantWidth(self.ImplantWidth)
            corner.setsolid(self.solid)
            corner.ShiTomasiCorner(self.minDistance, self.qualityLevel, self.maxCorners)
            corner.UpdateJson(self.JsonFile)
            endtime = datetime.datetime.now()
            print("compute ImplantCorner Time: ", (endtime - starttime))

        endtime = datetime.datetime.now()
        print("compute circle Time: ", (endtime - starttime))


    def bubbleSort(self, arr):
        '''
        对检测出来的球新进行排序,按X数值由小到大进行排序
        比较X的数值的时候,如果X轴之间的数值差值小于1,则比较Y轴的数值,也是由小到大进行排序
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
    
    def ReadJson(self, filename = None, sort = True, ):
        if filename == None:
            filename = self.JsonFile
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                info_dict = json.load(f)
                n = min(len(self.preoperative), self.CircleNum)
                for i in range(n):
                    self.preoperative[i][0] = float(info_dict['preoperative']['MarkerPoints'][str(i + 1)]['x'])
                    self.preoperative[i][1] = float(info_dict['preoperative']['MarkerPoints'][str(i + 1)]['y'])
                    self.preoperative[i][2] = float(info_dict['preoperative']['MarkerPoints'][str(i + 1)]['z'])

                    self.postoperative[i][0] = float(info_dict['postoperative']['MarkerPoints'][str(i + 1)]['x'])
                    self.postoperative[i][1] = float(info_dict['postoperative']['MarkerPoints'][str(i + 1)]['y'])
                    self.postoperative[i][2] = float(info_dict['postoperative']['MarkerPoints'][str(i + 1)]['z'])
                
                if sort:
                    self.preoperative = self.bubbleSort(self.preoperative)
                    self.postoperative = self.bubbleSort(self.postoperative)
                # print("============preoperative=============================================================")
                # print(self.preoperative)

                # 加入术前术后的种植体的位置
                self.ImplantPosition[0][0] = float(info_dict['preoperative']['ImplantPoint']['x'])
                self.ImplantPosition[0][1] = float(info_dict['preoperative']['ImplantPoint']['y'])
                self.ImplantPosition[0][2] = float(info_dict['preoperative']['ImplantPoint']['z'])
                self.ImplantPosition[0][3] = float(info_dict['postoperative']['ImplantPoint']['x'])
                self.ImplantPosition[0][4] = float(info_dict['postoperative']['ImplantPoint']['y'])
                self.ImplantPosition[0][5] = float(info_dict['postoperative']['ImplantPoint']['z'])

                self.ImplantPosition[1][0] = float(info_dict['preoperative']['RootPoint']['x'])
                self.ImplantPosition[1][1] = float(info_dict['preoperative']['RootPoint']['y'])
                self.ImplantPosition[1][2] = float(info_dict['preoperative']['RootPoint']['z'])
                self.ImplantPosition[1][3] = float(info_dict['postoperative']['RootPoint']['x'])
                self.ImplantPosition[1][4] = float(info_dict['postoperative']['RootPoint']['y'])
                self.ImplantPosition[1][5] = float(info_dict['postoperative']['RootPoint']['z'])



                self.UpdateJson(filename)
            except:
                print("cannot read or update json file 202")
    
    def UpdateJson(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                info_dict = json.load(f)
                n = self.CircleNum
                for i in range(n):
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['x'] = str(self.preoperative[i][0])
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['y'] = str(self.preoperative[i][1])
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['z'] = str(self.preoperative[i][2])

                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['x'] = str(self.postoperative[i][0])
                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['y'] = str(self.postoperative[i][1])
                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['z'] = str(self.postoperative[i][2])                    
            except:
                print("cannot read or update json file 218")

        ## 将info_dict写入app.json文件
        with open(filename, 'w', encoding='utf-8') as f1:
            f1.write(json.dumps(info_dict, indent=4, ensure_ascii=False))


    def UpdateJson_five(self, filename = None):
        if filename == None:
            filename = self.JsonFile
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                info_dict = json.load(f)
                n = 5
                for i in range(n):
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['x'] = str(self.pre_five[i][0])
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['y'] = str(self.pre_five[i][1])
                    info_dict['preoperative']['MarkerPoints'][str(i + 1)]['z'] = str(self.pre_five[i][2])

                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['x'] = str(self.post_five[i][0])
                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['y'] = str(self.post_five[i][1])
                    info_dict['postoperative']['MarkerPoints'][str(i + 1)]['z'] = str(self.post_five[i][2])

                total = {0, 1, 2, 3, 4, 5, 6}
                pre_remain = list(total - self.pre_comb)
                post_remain = list(total - self.post_comb)
             
                info_dict['preoperative']['MarkerPoints'][str(6)]['x'] = str(self.preoperative[pre_remain[0]][0])
                info_dict['preoperative']['MarkerPoints'][str(6)]['y'] = str(self.preoperative[pre_remain[0]][1])
                info_dict['preoperative']['MarkerPoints'][str(6)]['z'] = str(self.preoperative[pre_remain[0]][2])
                info_dict['preoperative']['MarkerPoints'][str(7)]['x'] = str(self.preoperative[pre_remain[1]][0])
                info_dict['preoperative']['MarkerPoints'][str(7)]['y'] = str(self.preoperative[pre_remain[1]][1])
                info_dict['preoperative']['MarkerPoints'][str(7)]['z'] = str(self.preoperative[pre_remain[1]][2])

                info_dict['postoperative']['MarkerPoints'][str(6)]['x'] = str(self.postoperative[post_remain[0]][0])
                info_dict['postoperative']['MarkerPoints'][str(6)]['y'] = str(self.postoperative[post_remain[0]][1])
                info_dict['postoperative']['MarkerPoints'][str(6)]['z'] = str(self.postoperative[post_remain[0]][2])
                info_dict['postoperative']['MarkerPoints'][str(7)]['x'] = str(self.postoperative[post_remain[1]][0])
                info_dict['postoperative']['MarkerPoints'][str(7)]['y'] = str(self.postoperative[post_remain[1]][1])
                info_dict['postoperative']['MarkerPoints'][str(7)]['z'] = str(self.postoperative[post_remain[1]][2])

            except:
                print("cannot read or update json file 218")

        ## 将info_dict写入app.json文件
        with open(filename, 'w', encoding='utf-8') as f1:
            f1.write(json.dumps(info_dict, indent=4, ensure_ascii=False))


    def UpdateMpsFile(self, filename, dataType = "preoperative"):
        mpsdata = None

        if dataType == "preoperative":
            mpsdata = self.preoperative
        else:
            mpsdata = self.postoperative

        filename = filename + str(self.CircleNum) + ".mps"
        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(filename)
        collection = DOMTree.documentElement
        
        # 在集合中获取所有的配准点
        point_set = collection.getElementsByTagName("point")

        # 打印每个配准点的详细信息
        for point in point_set:
            id = point.getElementsByTagName('id')[0]
            id_data = id.childNodes[0].data
            x = point.getElementsByTagName('x')[0]
            y = point.getElementsByTagName('y')[0]
            z = point.getElementsByTagName('z')[0]
            # print("id %s: %s, %s, %s" %(id_data, x_data, y_data, z_data))

            # if (int(id_data) >= self.CircleNum):
            #     break

            x.childNodes[0].data = str(mpsdata[int(id_data)][0])
            y.childNodes[0].data = str(mpsdata[int(id_data)][1])
            z.childNodes[0].data = str(mpsdata[int(id_data)][2])

        Min = collection.getElementsByTagName("Min")
        Max = collection.getElementsByTagName("Max")
        # 获取标签的属性值username
        Min[0].setAttribute("x", str(np.min(mpsdata[:, 0])))
        Min[0].setAttribute("y", str(np.min(mpsdata[:, 1])))
        Min[0].setAttribute("z", str(np.min(mpsdata[:, 2])))

        Max[0].setAttribute("x", str(np.max(mpsdata[:, 0])))
        Max[0].setAttribute("y", str(np.max(mpsdata[:, 1])))
        Max[0].setAttribute("z", str(np.max(mpsdata[:, 2])))
        with open(filename, "w") as fh:
            DOMTree.writexml(fh)
    
    def UpdateExcel(self, filename, sheetName):
        A = np.concatenate((self.preoperative, self.postoperative), axis=1)
        B = np.concatenate((A, self.ImplantPosition), axis=0)
        data = pd.DataFrame(B)
        writer = pd.ExcelWriter(filename, mode='a', engine="openpyxl")		# 写入Excel文件
        data.to_excel(writer, sheetName, float_format='%.2f')		# ‘page_1’是写入excel的sheet名
        writer.save()
        writer.close()

    def arrayFromVTKMatrix(self, vmatrix):
        """Return vtkMatrix4x4 or vtkMatrix3x3 elements as numpy array.
        The returned array is just a copy and so any modification in the array will not affect the input matrix.
        To set VTK matrix from a numpy array, use :py:meth:`vtkMatrixFromArray` or
        :py:meth:`updateVTKMatrixFromArray`.
        """
        from vtk import vtkMatrix4x4
        from vtk import vtkMatrix3x3
        import numpy as np
        if isinstance(vmatrix, vtkMatrix4x4):
            matrixSize = 4
        elif isinstance(vmatrix, vtkMatrix3x3):
            matrixSize = 3
        else:
            raise RuntimeError("Input must be vtk.vtkMatrix3x3 or vtk.vtkMatrix4x4")
        narray = np.eye(matrixSize)
        vmatrix.DeepCopy(narray.ravel(), vmatrix)
        return narray

    def vtkMatrixFromArray(self, narray):
        """Create VTK matrix from a 3x3 or 4x4 numpy array.
        :param narray: input numpy array
        The returned matrix is just a copy and so any modification in the array will not affect the output matrix.
        To set numpy array from VTK matrix, use :py:meth:`arrayFromVTKMatrix`.
        """
        from vtk import vtkMatrix4x4
        from vtk import vtkMatrix3x3
        narrayshape = narray.shape
        if narrayshape == (4,4):
            vmatrix = vtkMatrix4x4()
            self.updateVTKMatrixFromArray(vmatrix, narray)
            return vmatrix
        elif narrayshape == (3,3):
            vmatrix = vtkMatrix3x3()
            self.updateVTKMatrixFromArray(vmatrix, narray)
            return vmatrix
        else:
            raise RuntimeError("Unsupported numpy array shape: "+str(narrayshape)+" expected (4,4)")

    def updateVTKMatrixFromArray(self, vmatrix, narray):
        """Update VTK matrix values from a numpy array.
        :param vmatrix: VTK matrix (vtkMatrix4x4 or vtkMatrix3x3) that will be update
        :param narray: input numpy array
        To set numpy array from VTK matrix, use :py:meth:`arrayFromVTKMatrix`.
        """
        from vtk import vtkMatrix4x4
        from vtk import vtkMatrix3x3
        if isinstance(vmatrix, vtkMatrix4x4):
            matrixSize = 4
        elif isinstance(vmatrix, vtkMatrix3x3):
            matrixSize = 3
        else:
            raise RuntimeError("Output vmatrix must be vtk.vtkMatrix3x3 or vtk.vtkMatrix4x4")
        if narray.shape != (matrixSize, matrixSize):
            raise RuntimeError("Input narray size must match output vmatrix size ({0}x{0})".format(matrixSize))
    
    def distanceToCenter(self, pointSet):
        dist_mat = spatial.distance_matrix(pointSet, pointSet)
        distance = np.sum(dist_mat)

        return distance

    def matrixError(self, pre, post):
        pSourcePoints = vtk.vtkPoints()           
        pTargetPoints = vtk.vtkPoints()

        # 求取术前空间到术后空间的转换矩阵
        for i in range(5):
            pTargetPoints.InsertPoint(i, post[i][0] ,  post[i][1] ,  post[i][2])
            pSourcePoints.InsertPoint(i, pre[i][0],  pre[i][1],  pre[i][2])

        landmarkTransform = vtk.vtkLandmarkTransform()
        landmarkTransform.SetSourceLandmarks(pSourcePoints)
        landmarkTransform.SetTargetLandmarks(pTargetPoints)
        landmarkTransform.SetModeToRigidBody()
        landmarkTransform.Update()
    
        matrix = landmarkTransform.GetMatrix()
        matrix_np = self.arrayFromVTKMatrix(matrix)

        temp_five = np.ones([5,3], dtype = float)
        temp_dist = []
        for i in range(5):
            post_temp = np.array([pre[i][0], pre[i][1], pre[i][2], 1])
            post_temp_transform = np.matmul(matrix_np, post_temp)

            temp_five[i] = post_temp_transform[0:3]
            dist = np.linalg.norm(post[i] - post_temp_transform[0:3])
            temp_dist.append(dist)

        # print("post ", post)
        # print("temp_five ", temp_five)
        # print("temp_dist ", temp_dist)

        temp_dist = np.array(temp_dist)

        # print("max error ", np.max(temp_dist))

        # 返回最大的偏差
        return np.max(temp_dist), matrix_np
  
    def selectOptimalPoint(self):
        # 计算术前marker点最合适的几个点
        comb = list(itertools.combinations([0,1,2,3,4,5,6],5))
        pre_index = 0      # comb数组的下标
        post_index = 0     # comb数组的下标
        min_error = float("inf")   #
        # pre_dist_list = [0] * len(comb)
        pre_dist_list = np.zeros([len(comb),])
        for i in range(len(comb)):
            pre_dist_list[i] = self.distanceToCenter(self.preoperative[np.array(comb[i])])
        

        sort_index_pre = np.argsort(np.array(pre_dist_list))
        print(pre_dist_list[sort_index_pre])
        pre_dist_list = pre_dist_list[sort_index_pre]

        diff_list = [0]

        for i in range(1, len(pre_dist_list) - 1, 1):
            if (abs(pre_dist_list[i] - pre_dist_list[i-1]) > 1 and abs(pre_dist_list[i] - pre_dist_list[i+1]) > 1 ):
                diff_list.append(i)
        
        diff_list.append(len(pre_dist_list) - 1)
        post_dist_list = np.zeros([len(comb),])

        for i in range(len(comb)):
            post_dist_list[i] = self.distanceToCenter(self.postoperative[np.array(comb[i])])
        
        # sort_index_post = np.argsort(np.array(post_dist_list))
        # print(post_dist_list[sort_index_post])
        # print("sort_index_post ", sort_index_post)

        diff_list = np.array(diff_list)
        diff_list_dist = pre_dist_list[diff_list]
        for i in range(len(comb)):
            dist_temp = post_dist_list[i]

            idx = np.abs(diff_list_dist - dist_temp).argmin()
            
            idx2 = diff_list[idx]
            pre_com = comb[sort_index_pre[idx2]]
            post_com = comb[i]

            dist_error, matrix = self.matrixError(self.preoperative[np.array(pre_com)], self.postoperative[np.array(post_com)])

            if dist_error < min_error:
                min_error = dist_error
                pre_index = sort_index_pre[idx2]
                post_index = i
                self.maxtrix_pre2post = matrix
        
        print("min dist_error", min_error)
        self.post_five = self.postoperative[np.array(comb[post_index])]
        self.pre_five = self.preoperative[np.array(comb[pre_index])]

        self.pre_comb = set(comb[pre_index])
        self.post_comb = set(comb[post_index])

        print("post ", self.post_five)
        print("pre ", self.pre_five)

        # 推测术后的理想位置
        root_position = np.array([self.ImplantPosition[1][0], self.ImplantPosition[1][1], self.ImplantPosition[1][2], 1])
        implant_position = np.array([self.ImplantPosition[0][0], self.ImplantPosition[0][1], self.ImplantPosition[0][2], 1])
        # implant_position = np.array([-21.1163098, -38.4432959, 2.1136597, 1])
        # root_position = np.array([-18.7132, -35.571, 11.386, 1])

        # Test = np.array([self.preoperative[3][0], self.preoperative[3][1], self.preoperative[3][2], 1])
        # Test2 =  np.matmul(self.maxtrix_pre2post, Test)

        self.implant_position = np.matmul(self.maxtrix_pre2post, implant_position)
        self.root_position = np.matmul(self.maxtrix_pre2post, root_position)
        print("理想的术后植入点 ", self.implant_position)
        print("理想的术后根尖点 ", self.root_position)
        # print("测试的数据", Test2)
        
          
    def distanceAndAngleCompute(self, num = 7):
        pSourcePoints = vtk.vtkPoints()           
        pTargetPoints = vtk.vtkPoints()

        # 求取术后空间到术前空间的转换矩阵
        for i in range(num):
            pTargetPoints.InsertPoint(i, self.preoperative[i][0] ,  self.preoperative[i][1] ,  self.preoperative[i][2])
            pSourcePoints.InsertPoint(i, self.postoperative[i][0],  self.postoperative[i][1],  self.postoperative[i][2])
        
        # 将种植体的植入点和跟尖点加入
        pSourcePoints.InsertPoint(num, self.ImplantPosition[0][3],  self.ImplantPosition[0][4],  self.ImplantPosition[0][5])
        pSourcePoints.InsertPoint(num + 1, self.ImplantPosition[1][3],  self.ImplantPosition[1][4],  self.ImplantPosition[1][5])

        pTargetPoints.InsertPoint(num, self.ImplantPosition[0][0],  self.ImplantPosition[0][1],  self.ImplantPosition[0][2])
        pTargetPoints.InsertPoint(num + 1, self.ImplantPosition[1][0],  self.ImplantPosition[1][1],  self.ImplantPosition[1][2])


        landmarkTransform = vtk.vtkLandmarkTransform()
        landmarkTransform.SetSourceLandmarks(pSourcePoints)
        landmarkTransform.SetTargetLandmarks(pTargetPoints)
        landmarkTransform.SetModeToRigidBody()
        landmarkTransform.Update()
    
        matrix = landmarkTransform.GetMatrix()
        
        matrix_np = self.arrayFromVTKMatrix(matrix)

        for i in range(4):
            for j in range(4):
                print("{:10.7f}".format(matrix.GetElement(i, j)) , end=", ")
            print("")

        post_root = np.array([self.ImplantPosition[1][3], self.ImplantPosition[1][4], self.ImplantPosition[1][5], 1])
        post_implant = np.array([self.ImplantPosition[0][3], self.ImplantPosition[0][4], self.ImplantPosition[0][5], 1])

        
        # print("术后植入点 ", post_implant)
        # print("术后跟尖点 ", post_root)

        post_implant = np.matmul(matrix_np, post_implant)
        post_root = np.matmul(matrix_np, post_root)

        post_implant = post_implant[0:3]
        post_root = post_root[0:3]

        pre_root = np.array([self.ImplantPosition[1][0], self.ImplantPosition[1][1], self.ImplantPosition[1][2]])
        pre_implant = np.array([self.ImplantPosition[0][0], self.ImplantPosition[0][1], self.ImplantPosition[0][2]])

        print("术前植入点 ", pre_implant)
        print("术前跟尖点 ", pre_root)

        print("术后植入点 ", post_implant)
        print("术后跟尖点 ", post_root)

        print("植入点之间的距离偏差 " , np.linalg.norm(pre_implant - post_implant))
        print("根尖点之间的距离偏差 " , np.linalg.norm(pre_root - post_root))

        angle = vtk.vtkMath().AngleBetweenVectors(pre_root - pre_implant, post_root - post_implant)
        print("角度偏差 ", math.degrees(angle))
        print(Style.RESET_ALL)

        
if __name__ == '__main__':
    # inputDirectory = "E:/Teeth/PostVerify/model_2/Image"
    # inputDirectory = "E:/Teeth/nanjing/04.22 CHENYAN 14/Image"
    # inputDirectory = "E:/Teeth/nanjing/CHENYAN2/CHENYAN/I"

    inputDirectory =   "E:/Teeth/nanjing/20220427/post"
    outputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect"

    starttime = datetime.datetime.now()
    verify = SurgicalVerify(inputDirectory, outputDirectory)
    # verify.setsortThreshold(3)
    verify.setImplantWidth(4.1)
    verify.setImplantLength(10)
    verify.setImplantArea("14")
    verify.setdetectImplant(True)
    verify.setJsonFile('operativedata.json')
    verify.ReadJson('operativedata.json')
    # verify.setOperativeStage('preoperative')
    verify.setOperativeStage('postoperative')
    verify.setsolid(True)
    verify.AutoDetect()
    # verify.ReadJson('operativedata.json')
    verify.UpdateMpsFile('MarkerPoint', "postoperative")
    verify.UpdateJson_five()
    endtime = datetime.datetime.now()
    print("Compute Time: ", (endtime - starttime))

    # verify.distanceAndAngleCompute()
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    # verify.setJsonFile('operativedata.json')