# VMTK读取图像
from vmtk import pypes
from vmtk import vmtkscripts

#读取Dicom序列
DicomShow = 'vmtkimagereader -ifile \"C:/Users/chenjiaxing/Desktop/Python/DICOM/0.dcm\" --pipe vmtkimageviewer'

#读取mha图像
mhaRead = 'vmtkimagereader -ifile data\Aorta_voi.mha --pipe vmtkimageviewer'


myPype = pypes.PypeRun(mhaRead)