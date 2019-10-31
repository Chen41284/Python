# 使用给定的阈值显示图像特定的区域
# import os
# from vmtk import pypes
# from vmtk import vmtkscripts
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimageviewer as imageviewer
import vmtk.vmtkimageotsuthresholds as otsu

# 读取PNG图像 使用otsuthresholds 大津算法
def ostsuerThreshold():
    input_datadir = 'C:/Users/chenjiaxing/Desktop/CT-Data/png/Spine_Bone_Ext/'
    reader = imagereader.vmtkImageReader()

     # 单幅图像
    # reader.InputFileName = os.path.join(input_datadir, '170.png')
    
     # 图像序列
    reader.InputFilePrefix = input_datadir
    reader.InputFilePattern = "%s%d.png"
    reader.DataExtent = [0 ,512 ,0, 512, 1, 188]
    reader.Format = "png"
    reader.UseITKIO = 0
    reader.Execute()

    otsuer = otsu.vmtkImageOtsuThresholds()
    otsuer.Image = reader.Image
    otsuer.NumberOfThresholds = 2
    otsuer.Execute()

    viewer = imageviewer.vmtkImageViewer()
    viewer.Image = otsuer.Image
    viewer.Execute()

if __name__ == '__main__':
    ostsuerThreshold()