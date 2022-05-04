from __future__ import print_function

import SimpleITK as sitk
import matplotlib.pyplot as plt
import sys, time, os
from PIL import Image
import numpy as np
from numpy.core.records import array
import shutil

import threading

from sklearn.exceptions import NonBLASDotWarning
import concurrent.futures
import datetime
# import cupy as cp
import threading

class pngThread (threading.Thread):
    def __init__(self, image, direction, outputDirectory, intercept, slope,
                 window_center, window_width, origin, imageDirection, imageSpacing):
        threading.Thread.__init__(self)
        self.Image = image
        self.direction = direction
        self.outputDirectory = outputDirectory
        self.intercept = intercept
        self.slope = slope
        self.window_center = window_center
        self.window_width = window_width
        self.origin = origin
        self.imageDirection = imageDirection
        self.imageSpacing = imageSpacing
    
    def createDir(self, TEMP_PATH):
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, True)
            if os.path.exists(TEMP_PATH) == False: # 可能无法删除目录
                os.makedirs(TEMP_PATH)
        else:
            os.makedirs(TEMP_PATH)
        return True

    def run(self):
        print("self.direction ", self.direction)
        array = self.Image
        array2 = None
        if self.direction == "Z":
            array2 = array                           # 横断面
        elif self.direction == "X":
            array2 = array.transpose(2, 0, 1)        # 矢状面   numpy的循序和3D图像不同，实际对应位 (1, 0, 2)，刚好对应为矢状面
        elif self.direction == "Y":
            array2 = array.transpose(1, 2 ,0)        # 冠状面    
        else:
            print("unknow direction")
            return                  
        spacing = self.imageSpacing
        itk_image2 = sitk.GetImageFromArray(array2)
        itk_image2.SetOrigin(self.origin)
        if self.direction == "Z":
            itk_image2.SetSpacing(spacing)            # 横断面
        elif self.direction == "X":
            itk_image2.SetSpacing([spacing[2], spacing[0], spacing[1]])        # 矢状面
        else:
            itk_image2.SetSpacing([spacing[1], spacing[2], spacing[0]])        # 冠状面
        itk_image2.SetDirection(self.imageDirection)
        array2 = sitk.GetArrayFromImage(itk_image2)

        array3 = np.swapaxes(array2, 0, 2)
        number = array3.shape[2]

        rotate_time = 0
        outputDirection = self.outputDirectory
        if self.direction == "Z":
            outputDirection = outputDirection + "/Axial/"        # 横断面
            rotate_time = 3
        elif self.direction == "X":
            outputDirection = outputDirection + "/Sagittal/"     # 矢状面
            rotate_time = 1
        else:
            outputDirection = outputDirection + "/Coronal/"      # 冠状面
            rotate_time = 2

        self.createDir(outputDirection)

        self.ImageTojpeg = array3
        for n in range(number):
            img = array3[:, :, n]
            rotated_img = np.rot90(img , rotate_time )

            pix = rotated_img
            window_center = self.window_center  # 窗位
            window_width = self.window_width  # 窗宽                #调整为和原始图像接近，使用400
            # 计算pix为ct值
            ct = pix * float(self.slope) + float(self.intercept)
            # 计算色阶值
            ct = ((ct - window_center) / window_width + 0.5) * 255
            # 消除大于最大ct值的数值，设为窗口最大值
            ct = np.where(ct > 255, 255, ct)
            # W消除小于最小ct值的数值，设为窗口最小值
            ct = np.where(ct < 0, 0, ct)


            # 横断面和冠状面的时候需要反转图像
            if self.direction == "Z" or self.direction == "Y":
                flip_img = Image.fromarray(ct).convert('L').transpose(Image.FLIP_LEFT_RIGHT)
                flip_img.save(outputDirection + str('%04d' % ( n ) ) + ".png")
            else:
                Image.fromarray(ct).convert('L').save( outputDirection + str('%04d' % ( n ) ) + ".png")
        
        print("finish ", self.direction)

class DicomToPNG:
    def __init__(self, inputDirectory : str, outputDirectory: str) -> None:
        self.inputDirectory = inputDirectory
        self.outputDirectory = outputDirectory
        self.series_reader = sitk.ImageSeriesReader()
        self.writer = sitk.ImageFileWriter()
        self.Image = None
        self.window_center = 0
        self.window_width = 2000
        self.ImageTojpeg = None

        # 测试使用的临时变量
        self.rotate_time = None
        self.slope = None
        self.intercept = None
        self.direction = None
        self.outputDirection = None

        # 全局的Image图像
        self.Image_Axial = None
        self.Image_Sagittal = None
        self.Image_Coronal = None
        self.mutex = threading.Lock()
        self.Image_Direction = None

    def readImage(self) -> None:
        series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(self.inputDirectory)
        if not series_IDs:
            print("ERROR: given directory \"" + self.inputDirectory + "\" does not contain a DICOM series.")
            sys.exit(1)
        series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(self.inputDirectory, series_IDs[0])
        self.series_reader.SetFileNames(series_file_names)
        self.series_reader.MetaDataDictionaryArrayUpdateOn()
        self.series_reader.LoadPrivateTagsOn()
        self.Image = self.series_reader.Execute()

        # Modify the image (blurring)
        # self.Image = sitk.DiscreteGaussian(image3D)

    def GetImage(self):
        return self.Image

    def GetImageAxial(self):
        return self.Image_Axial

    def GetImageSagittal(self):
        return self.Image_Sagittal

    def GetImageCoronal(self):
        return self.Image_Coronal
    
    def GetImageOrigin(self):
        return self.Image.GetOrigin()
    
    def GetImageSpacing(self):
        return self.Image.GetSpacing()
    
    def setWindowCenter(self, value : int):
        self.window_center = value
    
    def setWindowWidth(self, value : int):
        self.window_width = value

    def writePngFile(self, index):
        img = self.ImageTojpeg[:, :, index]
        rotated_img = np.rot90(img , self.rotate_time)

        pix = rotated_img
        window_center = self.window_center  # 窗位
        window_width = self.window_width  # 窗宽
        ct = pix * float(self.slope) + float(self.intercept)
        ct = ((ct - window_center) / window_width + 0.5) * 255
        ct = np.where(ct > 255, 255, ct)
        ct = np.where(ct < 0, 0, ct)
        # 横断面和冠状面的时候需要反转图像
        if self.direction == "Z" or self.direction == "Y":
            flip_img = Image.fromarray(ct).convert('L').transpose(Image.FLIP_LEFT_RIGHT)
            flip_img.save(self.outputDirection + str('%04d' % ( index ) ) + ".png")
        else:
            Image.fromarray(ct).convert('L').save( self.outputDirection + str('%04d' % ( index ) ) + ".png")

    # def writePngFileCuda(self, index):
    #     img = self.ImageTojpeg[:, :, index]
    #     img_cp = cp.asarray(img)
    #     rotated_img = cp.rot90(img_cp , self.rotate_time)

    #     pix = rotated_img
    #     window_center = self.window_center  # 窗位
    #     window_width = self.window_width  # 窗宽
    #     ct = pix * float(self.slope) + float(self.intercept)
    #     ct = ((ct - window_center) / window_width + 0.5) * 255
    #     ct = cp.where(ct > 255, 255, ct)
    #     ct = cp.where(ct < 0, 0, ct)
    #     ct = ct.astype(cp.uint8)
    #     ct = cp.asnumpy(ct)
    #     # 横断面和冠状面的时候需要反转图像
    #     if self.direction == "Z" or self.direction == "Y":
    #         flip_img = Image.fromarray(ct).convert('L').transpose(Image.FLIP_LEFT_RIGHT)
    #         flip_img.save(self.outputDirection + str('%04d' % ( index ) ) + ".png")
    #     else:
    #         Image.fromarray(ct).convert('L').save( self.outputDirection + str('%04d' % ( index ) ) + ".png")

    def writeImage(self, index):
        img = self.ImageTojpeg[:, :, index]
        rotated_img = np.rot90(img , self.rotate_time)

        window_center = self.window_center  # 窗位
        window_width = self.window_width  # 窗宽
        ct = rotated_img * float(self.slope) + float(self.intercept)
        ct = ((ct - window_center) / window_width + 0.5) * 255
        ct = np.where(ct > 255, 255, ct)
        ct = np.where(ct < 0, 0, ct)
        ct = ct.astype(np.uint8)
        # 横断面和冠状面的时候需要反转图像
        if self.direction == "Z" or self.direction == "Y":
            ct = np.fliplr(ct)
        
        if self.Image_Direction == "Axial":
            self.Image_Axial[:, :, index] = ct
        elif self.Image_Direction == "Sagittal":
            self.Image_Sagittal[:, :, index] = ct
        elif self.Image_Direction == "Coronal":
            self.Image_Coronal[:, :, index] = ct
        else:
            pass

    # def writeImageCuda(self, index):
    #     img = self.ImageTojpeg[:, :, index]
    #     rotated_img = cp.rot90(img , self.rotate_time)

    #     window_center = self.window_center  # 窗位
    #     window_width = self.window_width  # 窗宽
    #     ct = rotated_img * float(self.slope) + float(self.intercept)
    #     ct = ((ct - window_center) / window_width + 0.5) * 255
    #     ct = cp.where(ct > 255, 255, ct)
    #     ct = cp.where(ct < 0, 0, ct)
    #     ct = ct.astype(cp.uint8)
    #     # 横断面和冠状面的时候需要反转图像
    #     if self.direction == "Z" or self.direction == "Y":
    #         ct = cp.fliplr(ct)
        
    #     # print("sum of ct ", ct.sum())
    #     if self.Image_Direction == "Axial":
    #         self.Image_Axial[:, :, index] = ct
    #     elif self.Image_Direction == "Sagittal":
    #         self.Image_Sagittal[:, :, index] = ct
    #     elif self.Image_Direction == "Coronal":
    #         self.Image_Coronal[:, :, index] = ct
    #     else:
    #         pass

    def writePNGseries(self):
        # print("DicomToPNG: writePNGseries")

        # imageArray = sitk.GetArrayFromImage(self.Image)
        # imageArray2 = imageArray.copy()
        # imageArray3 = imageArray.copy()

        # intercept = self.series_reader.GetMetaData(0, "0028|1052")
        # slope = self.series_reader.GetMetaData(0, "0028|1053")
        # window_center = self.window_center  # 窗位
        # window_width = self.window_width  # 窗宽                    #调整为和原始图像接近，使用400
        # spacing = self.Image.GetSpacing()
        # origin = self.Image.GetOrigin()
        # imageDirection = self.Image.GetDirection()

        # threadX = pngThread(imageArray, "X", self.outputDirectory, intercept, slope, window_center, window_width, origin, imageDirection, spacing)
        # threadY = pngThread(imageArray2, "Y", self.outputDirectory, intercept, slope, window_center, window_width, origin, imageDirection, spacing)
        # threadZ = pngThread(imageArray3, "Z", self.outputDirectory, intercept, slope, window_center, window_width, origin, imageDirection, spacing)

        # # 开启新线程
        # threadX.start()
        # threadY.start()
        # threadZ.start()

        # threadZ.join()
        # threadX.join()
        # threadY.join()

        print("window_center ", self.window_center)
        print("window_width", self.window_width)
        self.slice("Z")         # 横断面
        self.slice("X")         # 矢状面
        self.slice("Y")         # 冠状面



    def createDir(self, TEMP_PATH):
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH, True)
            if os.path.exists(TEMP_PATH) == False: # 可能无法删除目录
                os.makedirs(TEMP_PATH)
        else:
            os.makedirs(TEMP_PATH)
        return True

    def slice(self, direction : str = "Z"):
        # itk_image = self.Image
        starttime = datetime.datetime.now()
        array = sitk.GetArrayFromImage(self.Image)
        array2 = None
        if direction == "Z":
            array2 = array                           # 横断面
        elif direction == "X":
            array2 = array.transpose(2, 0, 1)        # 矢状面   numpy的循序和3D图像不同，实际对应位 (1, 0, 2)，刚好对应为矢状面
        elif direction == "Y":
            array2 = array.transpose(1, 2 ,0)        # 冠状面    
        else:
            print("unknow direction")
            return
        del array

        # CBCT图像的像素间隔相同, 不需要重新设置图像的方向和间隔

        # spacing = self.Image.GetSpacing()
        # itk_image2 = sitk.GetImageFromArray(array2)
        # itk_image2.SetOrigin(self.Image.GetOrigin())
        # if direction == "Z":
        #     itk_image2.SetSpacing(spacing)            # 横断面
        # elif direction == "X":
        #     itk_image2.SetSpacing([spacing[2], spacing[0], spacing[1]])        # 矢状面
        # else:
        #     itk_image2.SetSpacing([spacing[1], spacing[2], spacing[0]])        # 冠状面
        # itk_image2.SetDirection(self.Image.GetDirection())
        # array2 = sitk.GetArrayFromImage(itk_image2)
        # del itk_image2

        array3 = np.swapaxes(array2, 0, 2)
        intercept = self.series_reader.GetMetaData(0, "0028|1052")
        slope = self.series_reader.GetMetaData(0, "0028|1053")
        number = array3.shape[2]

        del array2

        rotate_time = 0
        outputDirection = self.outputDirectory
        if direction == "Z":
            outputDirection = outputDirection + "/Axial/"        # 横断面
            rotate_time = 3
            # self.Image_Axial = cp.zeros(array3.shape, dtype = np.uint8) 
            # self.Image_Direction = "Axial"
        elif direction == "X":
            outputDirection = outputDirection + "/Sagittal/"     # 矢状面
            rotate_time = 1
            # self.Image_Sagittal = cp.zeros(array3.shape, dtype = np.uint8)
            # self.Image_Direction = "Sagittal"
        else:
            outputDirection = outputDirection + "/Coronal/"      # 冠状面
            rotate_time = 2
            # self.Image_Coronal = cp.zeros(array3.shape, dtype = np.uint8)
            # self.Image_Direction = "Coronal"

        # isExists = os.path.exists(outputDirection)

        # if not isExists:
        #     os.makedirs(outputDirection)

        self.createDir(outputDirection)

        self.ImageTojpeg = array3.astype(np.int32)
        self.rotate_time = rotate_time
        self.slope = slope
        self.intercept = intercept
        self.direction = direction
        self.outputDirection = outputDirection
        index = list(range(0, number, 1))

        # with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
        #     executor.map(self.writePngFileCuda, index)

        with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
            executor.map(self.writePngFile, index)

        # with concurrent.futures.ThreadPoolExecutor() as executor: ## 默认为1
        #     executor.map(self.writeImageCuda, index)

        endtime = datetime.datetime.now()
        print("writePNGseries Time: ", direction,  (endtime - starttime))


    def print_Image_info(self):
        """ Prints SimpleITK image information
        :param itk_image: SimpleITK image object.
        """
        print("[INFO]: Shape : ", self.Image.GetSize())
        print("[INFO]: Spacing :  ", self.Image.GetSpacing())
        print("[INFO]: Origin : ", self.Image.GetOrigin())
        print("[INFO]: Direction : ",  self.Image.GetDirection())
        print("[INFO]: Pixel type : ",  self.Image.GetPixelIDTypeAsString())
        print("[INFO]: intercept : ",  self.series_reader.GetMetaData(0, "0028|1052"))
        print("[INFO]: slope : ",  self.series_reader.GetMetaData(0, "0028|1053"))
        print(type(self.Image.GetOrigin()))
        

    def print_tag_info(self):
        '''
        部分Tag可能不存在
        '''
        tags_to_print = {'0010|0010': 'Patient name: ', 
                    '0008|0060' : 'Modality: ',
                    '0008|0021' : 'Series date: ',
                    '0008|0080' : 'Institution name: ',
                    '0008|1050' : 'Performing physician\'s name: ',
                    '0028|1050' : 'Window Center: ',
                    '0028|1051' : 'Window Width: '
                    }
        for tag in tags_to_print:
            try:
                print(tags_to_print[tag] + self.series_reader.GetMetaData(0, tag))
            except: # Ignore if the tag isn't in the dictionary
                pass


if __name__ == '__main__':
    inputDirectory = "F:/TeethData/CBCTData/SliceData20220225/YAMU2"
    # inputDirectory = "F:/TeethData/CBCTData/pig/STO_Rotate/SE0"
    outputDirectory = "D:/project/SimpleITK/TargetDetect"
    dicom2png = DicomToPNG(inputDirectory, outputDirectory)
    dicom2png.readImage()
    dicom2png.print_Image_info()
    dicom2png.print_tag_info()
    # dicom2png.setWindowCenter(2715)
    # dicom2png.setWindowWidth(884)
    dicom2png.writePNGseries()