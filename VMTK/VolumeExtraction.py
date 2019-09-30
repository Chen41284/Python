# VMTK读取图像
from vmtk import pypes
from vmtk import vmtkscripts

# DICOM图像序列的截取
DicomExtration = 'vmtkimagereader -ifile \"C:/Users/chenjiaxing/Desktop/Python/DICOM/0.dcm\" --pipe \
                   vmtkimagevoiselector -ofile \"C:/Users/chenjiaxing/Desktop/Python/DICOM/image_volume_voi.vti\" '

myPype = pypes.PypeRun(DicomExtration)