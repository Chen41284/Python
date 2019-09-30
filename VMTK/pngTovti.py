# 提取PNG图像序列的特定区域，并将他们存储为VTI格式的文件
import os
import vmtk.vmtkimagereader as imagereader
import vmtk.vmtkimagewriter as imagewriter

# 读取PNG图像 使用otsuthresholds 大津算法
def pngToVti():
    input_datadir = 'C:/Users/chenjiaxing/Desktop/CT-Data/png/Spine_Bone_Ext/'
    outputFileName = 'vessel.vti'
    reader = imagereader.vmtkImageReader()
 
    # 图像序
    filelist = os.listdir(input_datadir)
    #print(len(filelist))
    reader.InputFilePrefix = input_datadir
    reader.InputFilePattern = "%s%d.png"
    reader.DataExtent = [0 ,512 ,0, 512, 1, len(filelist)]
    reader.Format = "png"
    reader.UseITKIO = 0
    reader.Execute()

    writer = imagewriter.vmtkImageWriter()
    writer.Image = reader.Image
    writer.Format = "vtkxml"
    writer.OutputFileName = outputFileName
    writer.WindowLevel = [150, 1200]  #窗宽和窗位
    writer.Execute()



if __name__=='__main__':
    pngToVti()