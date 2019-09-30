#!/usr/bin/env python

"""
"""
import os
import vtk



def ExtractComponent():
    # Read the image
    InputDir = 'C:\\Users\\chenjiaxing\\Desktop\\CT-Data\\png\\WU_Coronal\\'
    OutputDir = 'C:\\Users\\chenjiaxing\\Desktop\\CT-Data\\png\\WU_Coronal_Ext\\'
    filetype = '.png'
    filelist = os.listdir(InputDir)
    for files in filelist:
        InputFileName = os.path.join(InputDir, files)    #输入的的文件路径
        if os.path.isdir(InputFileName):       #如果是文件夹则跳过
            continue
        fileExt = os.path.splitext(files)[1]  #获取原文件的后缀
        if fileExt != '.png':   #文件的后缀不是png则跳过, 不能用is not
            print(fileExt)
            continue
        #读取图像
        readerFactory = vtk.vtkImageReader2Factory()
        reader = readerFactory.CreateImageReader2(InputFileName)
        reader.SetFileName(InputFileName)
        reader.Update()
        #提取红色通道的数据
        extractRedFilter = vtk.vtkImageExtractComponents()
        extractRedFilter.SetInputConnection(reader.GetOutputPort())
        extractRedFilter.SetComponents(0)
        extractRedFilter.Update()
        #输入图像
        OutputFileName = os.path.join(OutputDir, files)   #新的文件路径,因为是随机访问的，使用文件原来的名字以保持对应
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(OutputFileName)
        writer.SetInputData(extractRedFilter.GetOutput())
        writer.Write()


if __name__ == '__main__':
    ExtractComponent()