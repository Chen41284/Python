# This function is from https://github.com/rock-learning/pytransform3d/blob/7589e083a50597a75b12d745ebacaa7cc056cfbd/pytransform3d/rotations.py#L302
from gettext import translation
import SimpleITK as sitk
import numpy as np
import matplotlib as plt
import sys
import time
import os
import itertools
def rotation3d_XYZ(image, theta_x, theta_y, theta_z, translation = None, output_spacing = None, background_value=0.0):
    """
    This function rotates an image across each of the x, y, z axes by theta_x, theta_y, and theta_z degrees
    respectively and resamples it to be isotropic.
    :param image: An sitk 3D image
    :param theta_x: The amount of degrees the user wants the image rotated around the x axis
    :param theta_y: The amount of degrees the user wants the image rotated around the y axis
    :param theta_z: The amount of degrees the user wants the image rotated around the z axis
    :param output_spacing: Scalar denoting the isotropic output image spacing. If None, then use the smallest
                           spacing from original image.
    :return: The rotated image
    """
    output_direction = image.GetDirection()
    euler_transform = sitk.Euler3DTransform (image.TransformContinuousIndexToPhysicalPoint([(sz-1)/2.0 for sz in image.GetSize()]), 
                                             np.deg2rad(theta_x), 
                                             np.deg2rad(theta_y), 
                                             np.deg2rad(theta_z))
    if translation is not None and len(translation) == 3:
        euler_transform.SetTranslation(translation)

    # compute the resampling grid for the transformed image
    max_indexes = [sz-1 for sz in image.GetSize()]
    extreme_indexes = list(itertools.product(*(list(zip([0]*image.GetDimension(),max_indexes)))))
    extreme_points_transformed = [euler_transform.TransformPoint(image.TransformContinuousIndexToPhysicalPoint(p)) for p in extreme_indexes]
    
    output_min_coordinates = np.min(extreme_points_transformed, axis=0)
    output_max_coordinates = np.max(extreme_points_transformed, axis=0)
    
    # isotropic ouput spacing
    # if output_spacing is None:
    #   output_spacing = min(image.GetSpacing())
    # output_spacing = [output_spacing]*image.GetDimension()
    output_spacing = image.GetSpacing()  # CBCT图像三个方向的Spacing是相同的
                    
    output_origin = output_min_coordinates
    output_size = [int(((omx-omn)/ospc)+0.5)  for ospc, omn, omx in zip(output_spacing, output_min_coordinates, output_max_coordinates)]
    
    # direction cosine of the resulting volume is the identity (default)
    return sitk.Resample(image1 = image, 
                         size = output_size, 
                         transform = euler_transform.GetInverse(), 
                         interpolator = sitk.sitkLinear, 
                         outputOrigin = output_origin,
                         outputSpacing = output_spacing,
                         defaultPixelValue = background_value,
                         outputDirection = output_direction)

def writeImage(input : str, output : str, theta_x : float, theta_y : float, theta_z : float, translation = None):
    # if len(sys.argv) < 3:
    #     print("Usage: python " + __file__ +
    #         " <input_directory_with_DICOM_series> <output_directory>")
    #     sys.exit(1)

    # Read the original series. First obtain the series file names using the
    # image series reader.
    data_directory = input
    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
    if not series_IDs:
        print("ERROR: given directory \"" + data_directory +
            "\" does not contain a DICOM series.")
        sys.exit(1)
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(
        data_directory, series_IDs[0])

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

    filtered_image = rotation3d_XYZ(filtered_image, theta_x , theta_y , theta_z , translation)
    # Write the 3D image as a series
    # IMPORTANT: There are many DICOM tags that need to be updated when you modify
    #            an original image. This is a delicate opration and requires
    #            knowledge of the DICOM standard. This example only modifies some.
    #            For a more complete list of tags that need to be modified see:
    #                http://gdcm.sourceforge.net/wiki/index.php/Writing_DICOM

    writer = sitk.ImageFileWriter()
    # Use the study/series/frame of reference information given in the meta-data
    # dictionary and not the automatically generated information from the file IO
    writer.KeepOriginalImageUIDOn()

    # Copy relevant tags from the original meta-data dictionary (private tags are
    # also accessible).
    tags_to_copy = ["0010|0010",  # Patient Name
                    "0010|0020",  # Patient ID
                    "0010|0030",  # Patient Birth Date
                    "0020|000D",  # Study Instance UID, for machine consumption
                    "0020|0010",  # Study ID, for human consumption
                    "0008|0020",  # Study Date
                    "0008|0030",  # Study Time
                    "0008|0050",  # Accession Number
                    "0008|0060"  # Modality
                    ]

    modification_time = time.strftime("%H%M%S")
    modification_date = time.strftime("%Y%m%d")

    # Copy some of the tags and add the relevant tags indicating the change.
    # For the series instance UID (0020|000e), each of the components is a number,
    # cannot start with zero, and separated by a '.' We create a unique series ID
    # using the date and time.
    # Tags of interest:
    direction = filtered_image.GetDirection()
    series_tag_values = [
                            (k, series_reader.GetMetaData(0, k))
                            for k in tags_to_copy
                            if series_reader.HasMetaDataKey(0, k)] + \
                        [("0008|0031", modification_time),  # Series Time
                        ("0008|0021", modification_date),  # Series Date
                        ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                        ("0020|000e", "1.2.826.0.1.3680043.2.1125." +
                        modification_date + ".1" + modification_time),
                        # Series Instance UID
                        ("0020|0037",
                        '\\'.join(map(str, (direction[0], direction[3],
                                            direction[6],
                                            # Image Orientation (Patient)
                                            direction[1], direction[4],
                                            direction[7])))),
                        ("0008|103e",
                        series_reader.GetMetaData(0, "0008|103e")
                        + " Processed-SimpleITK")]  # Series Description

    for i in range(filtered_image.GetDepth()):
        image_slice = filtered_image[:, :, i]
        # Tags shared by the series.
        for tag, value in series_tag_values:
            image_slice.SetMetaData(tag, value)
        # Slice specific tags.
        #   Instance Creation Date
        image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))
        #   Instance Creation Time
        image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))
        #   Image Position (Patient)
        image_slice.SetMetaData("0020|0032", '\\'.join(
            map(str, filtered_image.TransformIndexToPhysicalPoint((0, 0, i)))))
        #   Instace Number
        image_slice.SetMetaData("0020|0013", str(i))

        # Write to the output directory and add the extension dcm, to force writing
        # in DICOM format.
        writer.SetFileName(os.path.join(output, str(i) + '.dcm'))
        writer.Execute(image_slice)

if __name__ == '__main__':
    inputDirectory = "F:/TeethData/CBCTData/SliceData20220407/CY14.NO1/6"
    outputDirectory = "F:/TeethData/CBCTData/SliceData20220407/Rotate"
    translation = [0, 0, 30]
    writeImage(inputDirectory, outputDirectory, 0, 180, 0, translation)