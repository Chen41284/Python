import cv2
import numpy as np
import os
import shutil
from sklearn.neighbors import NearestNeighbors
from scipy import spatial
import re
import json

from sqlalchemy import false, true

class CornerDetect():
    def __init__(self, inputDirectory : str, outputDirectory: str) -> None:
        self.InputDir = inputDirectory
        self.OutputDir = outputDirectory
        self.ImageSpacing = 0.3
        self.LengthVerify = True
        self.X_index = 0
        self.Y_index = 0
        self.Z_index = 0
        self.ImplantPosition = [0] * 3
        self.RootPosition = [0] * 3
        self.Corner_exist = True
        self.ImageOrigin = [-76.95,  -76.95, -60.15]
        self.ImplantArea = "16"
        self.Accuracy = 0.80
        self.ImplantLength = 10
        self.ImplantWidth = 4.1
        self.LengthAccuracy = 0.85
        self.WidthAccuracy = 0.7

        self.solid = False
        
    def setsolid(self, value):
        self.solid = value
    
    def setImageSpacing(self, value):
        self.ImageSpacing = value
    
    def setImplantWidth(self, value):
        self.ImplantWidth = value
    
    def setImplantLength(self, value):
        self.ImplantLength = value
    
    def setImageOrigin(self, value):
        self.ImageOrigin = value
    
    def setImplantArea(self, value):
        self.ImplantArea = value

    def setAccuracy(self, value):
        self.Accuracy = value
        self.LengthAccuracy = self.Accuracy + 0.05
        self.WidthAccuracy = self.Accuracy - 0.1

    def pixelCount(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _,thresh = cv2.threshold(gray,127,255,0)
        row, col = image.shape[0], image.shape[1]
        count = 0
        for i in range(row):
            for j in range(col):
                if thresh[i, j] > 100:
                    count = count + 1
        return count
            
    def createDir(self, TEMP_PATH):
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, True)
            os.makedirs(TEMP_PATH)
        else:
            os.makedirs(TEMP_PATH)
        return True
    
    def ImplantCorner(self, inputDir : str, direction="Sagittal"):
        ImplantPosition = [0] * 3
        RootPosition = [0] * 3
        pngDir = os.path.abspath(inputDir)
        filename = ""
        filelist = os.listdir(pngDir)  # 列出文件夹下所有的目录与文件

        file_index = 0
        valid = len(filelist) > 0
        if not valid:
            self.Corner_exist = False
            return ImplantPosition, RootPosition, False

        for i in range(0, len(filelist)):
            filePath = os.path.join(pngDir, filelist[i])
            if os.path.isfile(filePath):
                regex = re.compile(r'\d+')
                num = int(max(regex.findall(filelist[i])))
                if ((num > 0) and (direction in filelist[i])):
                    file_index = num
                    filename = filePath
                    break
        if filename == "":
            self.Corner_exist = False
            return ImplantPosition, RootPosition, False
        img = cv2.imread(filename)
        mask = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _,thresh = cv2.threshold(gray,127,255,0)   # 需要进行二值化，否则检测出来的轮廓会比较大
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dst = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        valid = len(contours) > 0
        if not valid:
            return ImplantPosition, RootPosition, False
        # 找到所有的轮廓
        ImplantLength = self.ImplantLength / self.ImageSpacing
        ImplantWidth = self.ImplantWidth / self.ImageSpacing
        idx = 0
        
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

        # 填充最大的轮廓
        mask = cv2.drawContours(mask, contours, idx, (255,255,0), 1)

        # 轮廓的长宽比
        rect = cv2.minAreaRect(contours[idx])
        box = cv2.boxPoints(rect)
        box = np.array(box, dtype = np.float)
        # cv2.drawContours(mask, [box], 0, (0, 0, 255), 1)

        index = np.argsort(box[:, 1])

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

        img_rot = None
        img_crop1 = None
        img_crop2 = None

        # 判断种植体的开口朝向，确定植入点和根尖点
        towards = "Up"
        M = None
        # print("angle ", angle)
        if abs(slope) > 1:  # 种植体的偏差角度不大，转为水平判断，此时angle一般小于45度,斜率大于1
            temp = abs(angle - 90) < 1e-5 or abs(angle) < 1e-5
            if not temp:
                if slope < 0:
                    M = cv2.getRotationMatrix2D(center, angle, 1)   # 正数，逆时针旋转
                else:
                    M = cv2.getRotationMatrix2D(center, (angle-90), 1)  # 负数，顺时针旋转
                img_rot = cv2.warpAffine(img2, M, (width2, height2))
            else:
                img_rot = img2

            center1 = [int(center[0]), int(center[1] - length / 4)]
            center2 = [int(center[0]), int(center[1] + length / 4)]            
            img_crop1 = cv2.getRectSubPix(img_rot, (int(width), int(length / 2) ), center1)
            img_crop2 = cv2.getRectSubPix(img_rot, (int(width), int(length / 2) ), center2)
            
            if (img_crop1 is None or img_crop2 is None):
                return ImplantPosition, RootPosition, False
                
            count1 = self.pixelCount(img_crop1)
            count2 = self.pixelCount(img_crop2)

            # print("count 1", count1)
            # print("count 2", count2)
            
            if count1 < count2:
                towards = "Up"
            else:
                towards = "Down"
            # print("towards", towards)
        else:
            temp = abs(angle - 90) < 1e-5 or abs(angle) < 1e-5
            if not temp:
                if slope < 0:
                    M = cv2.getRotationMatrix2D(center, (angle-90), 1)   # 正数，逆时针旋转
                else:
                    M = cv2.getRotationMatrix2D(center, angle, 1)  # 负数，顺时针旋转 
                img_rot = cv2.warpAffine(img2, M, (height2, width2))
            else:
                img_rot = img2

            center1 = [int(center[0] - length / 4), int(center[1])]
            center2 = [int(center[0] + length / 4), int(center[1])]            
            img_crop1 = cv2.getRectSubPix(img_rot, (int(length / 2), int(width) ), center1)
            img_crop2 = cv2.getRectSubPix(img_rot, (int(length / 2), int(width) ), center2)

            if (img_crop1 is None or img_crop2 is None):
                return ImplantPosition, RootPosition, False
            
            count1 = self.pixelCount(img_crop1)
            count2 = self.pixelCount(img_crop2)

            # print("count 1", count1)
            # print("count 2", count2)
            
            if count1 < count2:
                towards = "Left"
            else:
                towards = "Right"
        
        ImplantPoint = [0] * 2
        RootPoint = [0] * 2
        
        # 种植体的开口朝向
        if towards == "Up":
            index = np.argsort(box[:, 1])
            box = box[index]
            ImplantPoint[0] = (box[0][0] + box[1][0]) / 2
            ImplantPoint[1] = (box[0][1] + box[1][1]) / 2
            RootPoint[0] = (box[2][0] + box[3][0]) / 2
            RootPoint[1] = (box[2][1] + box[3][1]) / 2
        elif towards == "Down":
            index = np.argsort(box[:, 1])
            box = box[index]
            RootPoint[0] = (box[0][0] + box[1][0]) / 2
            RootPoint[1] = (box[0][1] + box[1][1]) / 2
            ImplantPoint[0] = (box[2][0] + box[3][0]) / 2
            ImplantPoint[1] = (box[2][1] + box[3][1]) / 2
        elif towards == "Left":
            index = np.argsort(box[:, 0])
            box = box[index]
            ImplantPoint[0] = (box[0][0] + box[1][0]) / 2
            ImplantPoint[1] = (box[0][1] + box[1][1]) / 2
            RootPoint[0] = (box[2][0] + box[3][0]) / 2
            RootPoint[1] = (box[2][1] + box[3][1]) / 2
        elif towards == "Right":
            index = np.argsort(box[:, 0])
            box = box[index]
            RootPoint[0] = (box[0][0] + box[1][0]) / 2
            RootPoint[1] = (box[0][1] + box[1][1]) / 2
            ImplantPoint[0] = (box[2][0] + box[3][0]) / 2
            ImplantPoint[1] = (box[2][1] + box[3][1]) / 2
        else:
            pass  
        
        if direction == "Sagittal":
            ImplantPosition[0] = file_index * self.ImageSpacing + self.ImageOrigin[0]
            ImplantPosition[1] = ImplantPoint[0] * self.ImageSpacing + self.ImageOrigin[1]
            ImplantPosition[2] = (img.shape[0] - ImplantPoint[1]) * self.ImageSpacing + self.ImageOrigin[2]

            RootPosition[0] = file_index * self.ImageSpacing + self.ImageOrigin[0]
            RootPosition[1] = RootPoint[0] * self.ImageSpacing + self.ImageOrigin[1]
            RootPosition[2] = (img.shape[0] - RootPoint[1]) * self.ImageSpacing + self.ImageOrigin[2]
        elif direction == "Coronal":
            ImplantPosition[0] = ImplantPoint[0] * self.ImageSpacing + self.ImageOrigin[0]
            ImplantPosition[1] = file_index * self.ImageSpacing + self.ImageOrigin[1]
            ImplantPosition[2] = (img.shape[0] - ImplantPoint[1]) * self.ImageSpacing + self.ImageOrigin[2]

            RootPosition[0] = RootPoint[0] * self.ImageSpacing + self.ImageOrigin[0]
            RootPosition[1] = file_index * self.ImageSpacing + self.ImageOrigin[1]
            RootPosition[2] = (img.shape[0] - RootPoint[1]) * self.ImageSpacing + self.ImageOrigin[2]
        elif direction == "Axial":
            ImplantPosition[0] = ImplantPoint[0] * self.ImageSpacing + self.ImageOrigin[0]
            ImplantPosition[1] = ImplantPoint[1] * self.ImageSpacing + self.ImageOrigin[1]
            ImplantPosition[2] = file_index * self.ImageSpacing + self.ImageOrigin[2]

            RootPosition[0] = RootPoint[0] * self.ImageSpacing + self.ImageOrigin[0]
            RootPosition[1] = RootPoint[1] * self.ImageSpacing + self.ImageOrigin[1]
            RootPosition[2] = file_index * self.ImageSpacing + self.ImageOrigin[2]
        else:
            pass

        print("towards", towards)
        print(direction)
        print("ImplantPosition ", ImplantPosition)
        print("RootPosition ", RootPosition)
        print("======================================")

        # 开口实心的情况下，种植体的植入点和根尖点需要反转
        if self.solid:
            return RootPosition, ImplantPosition, True
        else:
            return ImplantPosition, RootPosition, True    


    
    def ShiTomasiCorner(self, minDistance = 1, qualityLevel = 0.01, maxCorners = 100, nearestDist = 1):
        # pngDir = os.path.abspath(os.path.dirname(self.InputDir))
        pngDir = os.path.abspath(self.InputDir)

        ImplantPoition_S, RootPosition_S, bool_S = self.ImplantCorner(pngDir, "Sagittal")
        ImplantPoition_C, RootPosition_C, bool_C = self.ImplantCorner(pngDir, "Coronal")
        ImplantPoition_A, RootPosition_A, bool_A = self.ImplantCorner(pngDir, "Axial")

        if bool_S and bool_C:
            self.ImplantPosition[0] = ImplantPoition_C[0]
            self.ImplantPosition[1] = ImplantPoition_S[1]
            self.ImplantPosition[2] = (ImplantPoition_S[2] + ImplantPoition_C[2]) / 2

            self.RootPosition[0] = RootPosition_C[0]    
            self.RootPosition[1] = RootPosition_S[1]
            self.RootPosition[2] = (RootPosition_S[2] + RootPosition_C[2]) / 2
        elif bool_S and bool_A:
            self.ImplantPosition[0] = ImplantPoition_A[0]
            self.ImplantPosition[1] = (ImplantPoition_S[1] + ImplantPoition_A[1]) / 2
            self.ImplantPosition[2] = ImplantPoition_S[2]

            self.RootPosition[0] = RootPosition_A[0]    
            self.RootPosition[1] = (RootPosition_S[1] + RootPosition_A[1]) / 2
            self.RootPosition[2] = RootPosition_S[2]        
        elif bool_S:
            self.ImplantPosition[0] = ImplantPoition_S[0]
            self.ImplantPosition[1] = ImplantPoition_S[1]
            self.ImplantPosition[2] = ImplantPoition_S[2]

            self.RootPosition[0] = RootPosition_S[0]    
            self.RootPosition[1] = RootPosition_S[1]
            self.RootPosition[2] = RootPosition_S[2]
        elif bool_C:
            self.ImplantPosition[0] = ImplantPoition_C[0]
            self.ImplantPosition[1] = ImplantPoition_C[1]
            self.ImplantPosition[2] = ImplantPoition_C[2]

            self.RootPosition[0] = RootPosition_C[0]    
            self.RootPosition[1] = RootPosition_C[1]
            self.RootPosition[2] = RootPosition_C[2]
        elif bool_A:
            self.ImplantPosition[0] = ImplantPoition_A[0]
            self.ImplantPosition[1] = ImplantPoition_A[1]
            self.ImplantPosition[2] = ImplantPoition_A[2]

            self.RootPosition[0] = RootPosition_A[0]    
            self.RootPosition[1] = RootPosition_A[1]
            self.RootPosition[2] = RootPosition_A[2]
        else:
            pass         

        if bool_S or bool_C:
            self.Corner_exist = True 

        print("solid ", self.solid)
        if self.solid:
            print("开口为实心，交换植入点和根尖点")                  

        print("ImplantPosition ", self.ImplantPosition)
        print("RootPosition", self.RootPosition)

        ImplantPoint = []
        ImplantPoint.append(self.ImplantPosition)
        ImplantPoint.append(self.RootPosition)

        return ImplantPoint

    def UpdateJson(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                info_dict = json.load(f)
                if self.Corner_exist:
                    info_dict['postoperative']['ImplantPoint']['x'] = str(self.ImplantPosition[0])
                    info_dict['postoperative']['ImplantPoint']['y'] = str(self.ImplantPosition[1])
                    info_dict['postoperative']['ImplantPoint']['z'] = str(self.ImplantPosition[2])

                    info_dict['postoperative']['RootPoint']['x'] = str(self.RootPosition[0])
                    info_dict['postoperative']['RootPoint']['y'] = str(self.RootPosition[1])
                    info_dict['postoperative']['RootPoint']['z'] = str(self.RootPosition[2])
                else:
                    info_dict['postoperative']['ImplantPoint']['x'] = "not Implant"
                    info_dict['postoperative']['ImplantPoint']['y'] = "not Implant"
                    info_dict['postoperative']['ImplantPoint']['z'] = "not Implant"

                    info_dict['postoperative']['RootPoint']['x'] = "not Implant"
                    info_dict['postoperative']['RootPoint']['y'] = "not Implant"
                    info_dict['postoperative']['RootPoint']['z'] = "not Implant"                    
            except:
                print("cannot read or update json file")

        ## 将info_dict写入app.json文件
        with open(filename, 'w', encoding='utf-8') as f1:
            f1.write(json.dumps(info_dict, indent=4, ensure_ascii=False))



if __name__ == '__main__':
    inputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect/CornerDetect"
    outputDirectory = "D:/Lancet/TeethPostVerify/Local/TargetDetect/Classification"
    corner = CornerDetect(inputDirectory, outputDirectory)
    corner.ShiTomasiCorner(8, 0.01, 200)
    corner.UpdateJson('operativedata.json')
    corner.setsolid(true)
    cv2.waitKey(0)
    cv2.destroyAllWindows()