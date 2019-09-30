# 提取PNG图像序列的特定区域，并将他们存储为VTI格式的文件
import os
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimagewriter as imagewriter
import vmtk.vmtkimagevoiselector as imagevoiselector
def imagevoi(input_datadir, output_filename):
    '''
     提取图像感兴趣的区域
    '''
    print("Hello")
    reader = imagereader.vmtkImageReader()
 
    # 图像序
    filelist = os.listdir(input_datadir)
    #print(len(filelist))
    reader.InputFilePrefix = input_datadir
    reader.InputFilePattern = "%s%d.png"
    reader.DataExtent = [0, 512, 0, 512, 1, len(filelist)]
    reader.Format = "png"
    reader.UseITKIO = 0
    reader.Execute()

    selector = imagevoiselector.vmtkImageVOISelector()
    selector.Image = reader.Image
    selector.Execute()

    writer = imagewriter.vmtkImageWriter()
    writer.Image = selector.Image
    writer.Format = "vtkxml"
    writer.OutputFileName = output_filename
    writer.WindowLevel = [150, 1200]  #窗宽和窗位
    writer.Execute()


if __name__ == '__main__':
    input_datadir = 'C:/Users/chenjiaxing/Desktop/CT-Data/png/WU_Lung_Vessel_Ext/'
    output_filename = 'vesselVoi2.vtk'
    print('Hello')
    imagevoi(input_datadir, output_filename)