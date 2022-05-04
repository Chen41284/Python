from __future__ import print_function

import SimpleITK as sitk
import matplotlib.pyplot as plt
import sys, time, os
from PIL import Image
import numpy as np
from numpy.core.records import array

'''
if len( sys.argv ) < 3:
    print( "Usage: python " + __file__ + " <input_directory_with_DICOM_series> <output_directory>" )
    sys.exit ( 1 )
'''

# Read the original series. First obtain the series file names using the
# image series reader.
data_directory = "F:/TeethData/CBCTData/li wen hui"
output_directory = "F:/TeethData/CBCTData/ResliceTest"
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
if not series_IDs:
    print("ERROR: given directory \""+data_directory+"\" does not contain a DICOM series.")
    sys.exit(1)
series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory, series_IDs[0])

series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_names)

# Configure the reader to load all of the DICOM tags (public+private):
# By default tags are not loaded (saves time).
# By default if tags are loaded, the private tags are not loaded.
# We explicitly configure the reader to load tags, including the
# private ones.
series_reader.MetaDataDictionaryArrayUpdateOn()
series_reader.LoadPrivateTagsOn()
image3D = series_reader.Execute()

# Modify the image (blurring)
# filtered_image = sitk.DiscreteGaussian(image3D)
filtered_image = image3D

# Write the 3D image as a series
# IMPORTANT: There are many DICOM tags that need to be updated when you modify an
#            original image. This is a delicate opration and requires knowlege of
#            the DICOM standard. This example only modifies some. For a more complete
#            list of tags that need to be modified see:
#                           http://gdcm.sourceforge.net/wiki/index.php/Writing_DICOM

writer = sitk.ImageFileWriter()
# Use the study/series/frame of reference information given in the meta-data
# dictionary and not the automatically generated information from the file IO
writer.KeepOriginalImageUIDOn()

# Copy relevant tags from the original meta-data dictionary (private tags are also
# accessible).
tags_to_copy = ["0010|0010", # Patient Name
                "0010|0020", # Patient ID
                "0010|0030", # Patient Birth Date
                "0020|000D", # Study Instance UID, for machine consumption
                "0020|0010", # Study ID, for human consumption
                "0008|0020", # Study Date
                "0008|0030", # Study Time
                "0008|0050", # Accession Number
                "0008|0060"  # Modality
]

modification_time = time.strftime("%H%M%S")
modification_date = time.strftime("%Y%m%d")

# Copy some of the tags and add the relevant tags indicating the change.
# For the series instance UID (0020|000e), each of the components is a number, cannot start
# with zero, and separated by a '.' We create a unique series ID using the date and time.
# tags of interest:
direction = filtered_image.GetDirection()
series_tag_values = [(k, series_reader.GetMetaData(0,k)) for k in tags_to_copy if series_reader.HasMetaDataKey(0,k)] + \
                 [("0008|0031",modification_time), # Series Time
                  ("0008|0021",modification_date), # Series Date
                  ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                  ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                  ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                    direction[1],direction[4],direction[7])))),
                  ("0008|1070", series_reader.GetMetaData(0,"0008|1070") + " Processed-SimpleITK")] # Series Description


# filtered_image.GetSize()
# filtered_image.GetDepth()

'''
pa = sitk.PermuteAxesImageFilter()
pa.SetOrder([2,0,1])
filtered_image = pa.Execute(image3D)
'''

number = filtered_image.GetSize()[2]
print("number ", number)

def show_n_slices(array, start_from=0, step=10, columns=6, figsize=(18,10)):
    """ Plot N slices of a 3D image.
    :param array: N-dimensional numpy array (i.e. 3D image)
    :param start_from: slice index to start from
    :param step: step to take when moving to the next slice
    :param columns: number of columns in the plot
    :param figsize: figure size in inches
    """
    array = np.swapaxes(array, 0, 2)
    fig, ax = plt.subplots(1, columns, figsize=figsize)
    slice_num = start_from
    intercept = series_reader.GetMetaData(0, "0028|1052")
    slope = series_reader.GetMetaData(0, "0028|1053")
    print(type(slope))
    print(array.shape[2])
    for n in range(columns):
        img = array[:, :, slice_num]
        # rotated_img = img
        rotated_img = np.rot90(img , 1)

        # ax[n].imshow(array[:, :, slice_num], 'gray')
        ax[n].imshow(rotated_img, 'gray')
        ax[n].set_xticks([])
        ax[n].set_yticks([])
        ax[n].set_title('Slice number: {}'.format(slice_num), color='r')
        slice_num += step

        pix = rotated_img
        window_center = 0  # 窗位
        window_width = 2000  # 窗宽                #调整为和原始图像接近，使用400
        # 计算pix为ct值
        ct = pix * float(slope) + float(intercept)
        # 计算色阶值
        ct = ((ct - window_center) / window_width + 0.5) * 255
        # print("WL :" + str(wl) + " | WW :" + str(ww)  )
        # 消除大于最大ct值的数值，设为窗口最大值
        ct = np.where(ct > 255, 255, ct)
        # W消除小于最小ct值的数值，设为窗口最小值
        ct = np.where(ct < 0, 0, ct)

        Image.fromarray(ct).convert('L').save('%04d' % ( slice_num ) + ".jpeg")

    fig.subplots_adjust(wspace=0, hspace=0)
    plt.show()

def print_sitk_info(itk_image):
    """ Prints SimpleITK image information
    :param itk_image: SimpleITK image object.
    """
    print("[INFO]: Shape - {itk_image.GetSize()}")
    print("[INFO]: Spacing - {itk_image.GetSpacing()}")
    print("[INFO]: Origin - {itk_image.GetOrigin()}")
    print("[INFO]: Direction - {itk_image.GetDirection()}\n")

# print("[INFO]: Image Info before Resampling to Isotropic Resolution:")
# print_sitk_info(filtered_image)
# show_n_slices(sitk.GetArrayFromImage(filtered_image), start_from=20, step=5)

itk_image = filtered_image
array = sitk.GetArrayFromImage(filtered_image)
# array2 = array
# array2 = array.transpose(1, 2 ,0)                       # 冠状面
array2 = array.transpose(2, 0, 1)                     # 矢状面   numpy的循序和3D图像不同，实际对应位 (1, 0, 2)，刚好对应为矢状面
spacing = itk_image.GetSpacing()
itk_image2 = sitk.GetImageFromArray(array2)
# itk_image2.SetOrigin(itk_image.GetOrigin())
# itk_image2.SetSpacing([spacing[1], spacing[2], spacing[0]])   #冠状面
itk_image2.SetSpacing([spacing[2], spacing[0], spacing[1]])
itk_image2.SetSpacing(itk_image.GetSpacing())
itk_image2.SetDirection(itk_image.GetDirection())
array2 = sitk.GetArrayFromImage(itk_image2)

show_n_slices(array2, start_from=200, step=10)

intercept = series_reader.GetMetaData(0, "0028|1052")
slope = series_reader.GetMetaData(0, "0028|1053")
print("intercept", intercept)
print("slope", slope)