# -*- coding: utf-8 -*-
import SimpleITK as sitk
import os


def show_growing(image_data,index, file_growing):
    image = sitk.GetImageFromArray(image_data)
    castFilter = sitk.CastImageFilter()
    castFilter.SetOutputPixelType(sitk.sitkUInt8)
    image = castFilter.Execute(image)
    # sitk.Show(image)
    #[z, y, x] = image_data.shape
    [z, y, x] = image_data.shape
    #print('%-5d%-5d%-5d%-5d\n' % (index, x, y, z))
    #writerpath = "./JPEG_Growing/"+str(index)+"/"  # 分割出来的图像保存路径
    writerpath = file_growing + str(index)+ "/"
    if not os.path.exists(writerpath):
        os.makedirs(writerpath)
    filenames = []
    for i in range(z):
        tmpstr = writerpath + str(i) + '.jpg'
        filenames.append(tmpstr)
    sitk.WriteImage(image, filenames)

def show_edge(image_data, file_edge):
    image = sitk.GetImageFromArray(image_data)
    castFilter = sitk.CastImageFilter()
    castFilter.SetOutputPixelType(sitk.sitkUInt8)
    image = castFilter.Execute(image)
    # sitk.Show(image)
    #[z, y, x] = image_data.shape
    [z, y, x] = image_data.shape
    writerpath = file_edge  # 分割出来的图像保存路径
    filenames = []
    for i in range(z):
        tmpstr = writerpath + str(i) + '.jpg'
        filenames.append(tmpstr)
    sitk.WriteImage(image, filenames)