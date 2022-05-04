import cv2
import numpy as np
import os
# from skimage.measure._structural_similarity import compare_ssim
import shutil
import re
from skimage.metrics import structural_similarity as ssim
import concurrent.futures
import threading

from sqlalchemy import true

class ImplantDetect():
    def __init__(self, inputDirectory : str, outputDirectory: str) -> None:
        self.InputDir = inputDirectory
        self.OutputDir = outputDirectory
        self.ImplantArea = "46"
        self.ImplantLength = 10
        self.ImplantWidth = 4.1
        self.ImageSpacing = 0.3
        self.Accuracy = 0.65
        self.MaxAccuray = 0
        self.LengthVerify = True
        self.minSSIM = 0.30
        self.LengthAccuracy = 0.85
        self.WidthAccuracy = 0.80
        self.score_list = []
        self.filename_list = []

        self.multiVerify = True
        self.filter_x = -18.1469 + 76.95   # 减去原始点的位置偏移
        self.filter_y = -31.583 + 76.95    # 减去原始点的位置偏移
        self.filter_z = 6.46815 + 60.15    # 减去原始点的位置偏移

        self.num_score = {}
        
        # 并行计算使用的全局变量
        self.ImplantDir = None
        self.currentInputDir = None
        self.mutex = threading.Lock()
        self.max_score = 0
        self.max_score_file = None
        self.heightTemplate = None
        self.widthTemplate = None
        self.threshTemplate_Up = None
        self.threshTemplate_Down = None
        self.filelist_num = None
    
    def setMultiVerify(self, value):
        self.multiVerify = value

    def setfilter_x(self, value):
        self.filter_x = value

    def setfilter_y(self, value):
        self.filter_y = value

    def setfilter_z(self, value):
        self.filter_z = value

    def setImplantWidth(self, value):
        self.ImplantWidth = value
    
    def setImplantLength(self, value):
        self.ImplantLength = value
    
    def setImplantArea(self, value):
        self.ImplantArea = value
    
    def setImageSpacing(self, value):
        self.ImageSpacing = value

    def setAccuracy(self, value):
        self.Accuracy = value
        self.LengthAccuracy = self.Accuracy + 0.05
        self.WidthAccuracy = self.Accuracy - 0.1
    
    def setLengthVerify(self, value):
        self.LengthVerify = value
    
    def ImplantDetect(self):
        if not os.path.exists(self.InputDir):
            print("InputDir not exists")
            return
        if not os.path.exists(self.OutputDir):
            print("OutputDir not exists")
            return
        destDir = os.path.abspath(self.InputDir) + "/CornerDetect"
        self.createDir(destDir)

        # 横断面的检测
        AxialDir = self.InputDir + "/Axial"
        self.classify(AxialDir)
        self.SSIM_filter(AxialDir, "Axial")

        # 冠状面的检测
        CoronalDir = self.InputDir + "/Coronal"
        self.classify(CoronalDir)
        self.SSIM_filter(CoronalDir, "Coronal")

        # 矢状面的检测
        SagittalDir = self.InputDir + "/Sagittal"
        self.classify(SagittalDir)
        self.SSIM_filter(SagittalDir, "Sagittal")

        # 删除分数最低的所在面的种植体的图像
        if len(self.score_list) == 3:
            score = np.array(self.score_list, dtype = np.float) 
            index = np.argsort(score)
            os.remove(self.filename_list[index[0]])
    
    def classifyThreadPool(self, filename):
        if self.multiVerify:
            # 提前过滤不在检测范围内的种植体
            regex = re.compile(r'\d+')
            num = int(max(regex.findall(filename)))
            dist = num * self.ImageSpacing

            if "Axial" in self.currentInputDir:
                if ( abs(dist - self.filter_z) > self.ImplantLength):
                    return
            
            if "Sagittal" in self.currentInputDir:
                if ( abs(dist - self.filter_x) > self.ImplantWidth):
                    return
            
            if "Coronal" in self.currentInputDir:
                if ( abs(dist - self.filter_y) > self.ImplantWidth):
                    return


        fileInput = os.path.join(self.currentInputDir, filename)
        img = cv2.imread(fileInput)
        mask = img.copy()

        gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,127,255,0)   # 需要进行二值化，否则检测出来的轮廓会比较大
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dst = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        # 寻找轮廓
        contours, hierarchy = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        valid = len(contours) > 0
        if not valid:
            return

        ImplantLength = self.ImplantLength / self.ImageSpacing
        ImplantWidth = self.ImplantWidth / self.ImageSpacing
        idx = None
        # 寻找比例最接近的
        diff = float('inf')
        for k in range(len(contours)):
            rect = cv2.minAreaRect(contours[k])
            length = max(rect[1][0], rect[1][1])
            width = min(rect[1][0], rect[1][1])
            b1 = (length > ImplantLength * self.LengthAccuracy) and (length < (2 - self.LengthAccuracy) * ImplantLength)
            b2 = (width > ImplantWidth * self.WidthAccuracy) and (width < (2 - self.WidthAccuracy) * ImplantWidth)
            diff_temp = abs(length - ImplantLength)
            if b1 and b2 and (diff_temp < diff):
                idx = k
                diff = diff_temp
        
        if idx is None:
            return
        # 轮廓的长宽比
        rect = cv2.minAreaRect(contours[idx])
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        # cv2.drawContours(mask, [box], 0, (0, 0, 255), 1)

        output = cv2.fitLine(contours[idx], cv2.DIST_L2, 0, 0.01, 0.01)

        slope = output[1] / output[0]

        length = 1
        width = 1
        if (rect[1][0] > rect[1][1]):
            length = rect[1][0]
            width = rect[1][1]
        else:
            length = rect[1][1]
            width = rect[1][0]

        img2 = img.copy()

        center, size, angle = rect[0], rect[1], rect[2]
        center, size = tuple(map(int, center)), tuple(map(int, size))

        # get row and col num in img
        height2, width2 = img2.shape[0], img2.shape[1]

        # calculate the rotation matrix
        M = None       
        # 垂直的情况不进行旋转
        if abs(angle - 90) > 1e-4:  # 垂直的情况下，种植体刚好没有角度的旋转偏差
            if slope < 0:
                M = cv2.getRotationMatrix2D(center, angle, 1)
            else:
                M = cv2.getRotationMatrix2D(center, (angle-90), 1)
        else:
            if (abs(slope) < 1e-2):  # 水平横着的情况，真实情况也是这个，斜率接近于0
                M = cv2.getRotationMatrix2D(center, 90, 1)
            else:
                M = cv2.getRotationMatrix2D(center, 0, 1)
        
        # rotate the original image
        img_rot = cv2.warpAffine(img2, M, (width2, height2))

        # now rotated rectangle becomes vertical and we crop it
        img_crop = cv2.getRectSubPix(img_rot, (int(width), int(length) ), center)
        
        # print("angle and k", angle, slope)
        outputFile = os.path.join(self.ImplantDir, filename)
        cv2.imwrite(outputFile, img_crop)   #输出旋转后的模型
        # cv2.imwrite(outputFile, img)  

    def classify(self, inputDir : str):
        self.ImplantDir = self.OutputDir + "/Implant"
        self.createDir(self.ImplantDir)
        filelist = os.listdir(inputDir)  # 列出文件夹下所有的目录与文件
        self.currentInputDir = inputDir

        with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
            executor.map(self.classifyThreadPool, filelist)

            
    def createDir(self, TEMP_PATH):
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, True)
            os.makedirs(TEMP_PATH)
        else:
            os.makedirs(TEMP_PATH)
        return True
    
    def angle_between(self, v11, v22):
        v1 = np.array(v11)
        v2 = np.array(v22)

        Lx = np.sqrt(v1.dot(v1))
        Ly = np.sqrt(v2.dot(v2))

        if (Lx * Ly < 1e-4):
            return 0

        cos_angle = v1.dot(v2) / (Lx * Ly)
        angle = np.arccos(cos_angle)

        degree = angle * 360 / 2 / np.pi

        return degree

    def SSIMThreadPool(self, filename):
        regex = re.compile(r'\d+')
        num = int(max(regex.findall(filename)))
        pre = num - 1
        next = num + 1
        #左右两侧图像都不存在的时候，认为当前切片序列不是种植体中心
        if ((pre not in self.filelist_num) and (next not in self.filelist_num)):
            return

        fileInput = os.path.join(self.ImplantDir, filename)
        img = cv2.imread(fileInput)

        # 放缩图像  
        size = (int(self.widthTemplate), int(self.heightTemplate))  
        zoom = cv2.resize(img, size, interpolation=cv2.INTER_AREA) 
        img_zoom =cv2.cvtColor(zoom, cv2.COLOR_BGR2GRAY) #彩色转灰度
        _, threshzoom = cv2.threshold(img_zoom, 127, 255, 0)   #二值化

        score_Up = ssim(self.threshTemplate_Up, threshzoom, data_range=img.max() - img.min())
        score_Down = ssim(self.threshTemplate_Down, threshzoom, data_range=img.max() - img.min())
        score = max(score_Up, score_Down)

        if score < self.minSSIM:
            return

        self.num_score[num] = score
        if score > self.max_score:
            if self.mutex.acquire(True):
                self.max_score = score
                self.max_score_file = filename
                self.mutex.release()
    
    def SSIM_filter(self, inputDir : str, prefix="Sagittal"):

        template_file = os.path.abspath(os.path.dirname(inputDir)) + "/Template/"

        # 判断种植体开口朝下还是朝上
        template_file_Up = template_file + str(self.ImplantWidth) + "-" + str(self.ImplantLength) + "_Up.png"
        template_file_Down = template_file + str(self.ImplantWidth) + "-" + str(self.ImplantLength) + "_Down.png"
        if not os.path.exists(template_file_Up):
            print("{} is not exists".format(template_file_Up))
            return
        if not os.path.exists(template_file_Down):
            print("{} is not exists".format(template_file_Down))
            return
        
        img_Template_Up = cv2.imread(template_file_Up)
        img_Template_Up = cv2.cvtColor(img_Template_Up, cv2.COLOR_BGR2GRAY) #彩色转灰度
        _, self.threshTemplate_Up = cv2.threshold(img_Template_Up, 127, 255, 0)   #二值化
        img_Template_Down = cv2.imread(template_file_Down)
        img_Template_Down = cv2.cvtColor(img_Template_Down, cv2.COLOR_BGR2GRAY) #彩色转灰度
        _, self.threshTemplate_Down = cv2.threshold(img_Template_Down, 127, 255, 0)   #二值化
        self.heightTemplate, self.widthTemplate = self.threshTemplate_Up.shape[0], self.threshTemplate_Up.shape[1]

        ImplantDir = self.OutputDir + "/Implant"
        filelist = os.listdir(ImplantDir)  # 列出文件夹下所有的目录与文件
        self.max_score = 0
        self.max_score_file = None

        regex = re.compile(r'\d+')
        self.filelist_num = []

        if (len(filelist) == 0):
            print("no file")
            return

        for i in range(0, len(filelist)):
            num = int(max(regex.findall(filelist[i])))
            if num > 0:
                self.filelist_num.append(num)


        self.num_score.clear()
        with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
            executor.map(self.SSIMThreadPool, filelist)
        
        if self.max_score_file is not None:

            temp_sum = []
            keys = self.num_score.keys() 
            for key in keys:
                if abs(self.num_score.get(key) - self.max_score) < 0.2:
                    temp_sum.append(key)
            
            temp_sum = np.array(temp_sum)
            temp_middle = int(np.median(temp_sum))
            # print("temp_sum", temp_sum)
            # print("temp_middle", temp_middle)

            # print("SSIM: {}, {}, {}".format(prefix, self.max_score_file, self.max_score))

            
            print("SSIM: {}, {}, {}".format(prefix, str(temp_middle), self.max_score))

            temp_middle_file = str('%04d' % ( temp_middle ) ) + ".png"

            # sourcePath = os.path.join(inputDir, self.max_score_file)
            sourcePath = os.path.join(inputDir, temp_middle_file)
            destDir = os.path.abspath(os.path.dirname(inputDir)) + "/CornerDetect/"
            # self.createDir(destDir)
            # destPath = destDir + prefix + "_" + self.max_score_file
            destPath = destDir + prefix + "_" + temp_middle_file
            shutil.copy(sourcePath, destPath)
            self.score_list.append(self.max_score)
            self.filename_list.append(destPath)
        
        # print(self.num_score)

if __name__ == '__main__':
    inputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect"
    outputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect/Classification"
    detect = ImplantDetect(inputDirectory, outputDirectory)
    detect.setImplantArea("46")
    detect.setImplantLength(10)
    detect.setImplantWidth(4.1)
    # detect.setLengthVerify(False)
    # detect.classify()
    # detect.SSIM_filter()
    detect.ImplantDetect()