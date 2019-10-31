import os
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimageviewer as imageviewer
import vmtk.vmtkimageobjectenhancement as imageEnhance
# 计算特征图像以用于分割
def imageObjectEnhance():
    input_datadir = 'C:/Users/chenjiaxing/Desktop/CT-Data/png/WU_Lung_Vessel_Ext/'
    reader = imagereader.vmtkImageReader()
 
    # 图像序
    filelist = os.listdir(input_datadir)
    reader.InputFilePrefix = input_datadir
    reader.InputFilePattern = "%s%d.png"
    reader.DataExtent = [0, 512, 0, 512, 1, len(filelist)]
    reader.Format = "png"
    reader.UseITKIO = 0
    reader.Execute()

    imageObjEn = imageEnhance.vmtkImageObjectEnhancement()
    imageObjEn.Image = reader.Image
    # default arguments
    imageObjEn.SigmaMin = 1.0
    imageObjEn.SigmaMax = 1.0
    imageObjEn.NumberOfSigmaSteps = 1
    imageObjEn.ScaledObjectness = 0
    imageObjEn.Alpha = 0.5
    imageObjEn.Beta = 0.5
    imageObjEn.Gamma = 5.0
    imageObjEn.ObjectDimension = 2
    imageObjEn.Execute()

    viewer = imageviewer.vmtkImageViewer()
    viewer.Image = imageObjEn.Image
    viewer.Execute()
if __name__=='__main__':
    imageObjectEnhance()