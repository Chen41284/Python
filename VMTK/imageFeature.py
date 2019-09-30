import os
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimageviewer as imageviewer
import vmtk.vmtkimagefeatures as imageFeatures
def imagefeature():
    '''
    图像的水平集分割，生成等值面
    '''
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

    feature = imageFeatures.vmtkImageFeatures()
    feature.Image = reader.Image
    feature.FWHMRadius = [0.5, 0.5, 0.5]
    feature.FeatureImageType = "gradient"   # '["vtkgradient","gradient","upwind","fwhm"]'
    feature.Execute()

    viewer = imageviewer.vmtkImageViewer()
    viewer.Image = reader.Image
    viewer.Execute()
if __name__ == '__main__':
    imagefeature()