import os
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimageviewer as imageviewer
import vmtk.vmtkimagevesselenhancement as imagevesseEnhance
import vtk.vtkRenderingCore
# 图像的水平集分割，生成等值面
def imageFeature():
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


    imageVesselEnhance = imagevesseEnhance.vmtkImageVesselEnhancement()
    imageVesselEnhance.Image = reader.Image
    imageVesselEnhance.Method = "vedm"    #["frangi","sato","ved","vedm"]
    imageVesselEnhance.SigmaStepMethod = "equispaced"  #["equispaced","logarithmic"]
    imageVesselEnhance.Execute()

    viewer = imageviewer.vmtkImageViewer()
    viewer.Image = imageVesselEnhance.Image
    viewer.Execute()
if __name__=='__main__':
    imageFeature()