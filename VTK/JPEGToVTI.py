#!/usr/bin/env python

# This example reads a volume dataset, extracts two isosurfaces that
# represent the skin and bone, creates three orthogonal planes
# (sagittal, axial, coronal), and displays them.

import vtk

file_path = "C:\\Users\\chenjiaxing\\Desktop\\p4"
reader = vtk.vtkJPEGReader()
reader.SetFilePrefix(file_path)
reader.SetFilePattern("%s/%d.jpg")
reader.SetDataExtent(0, 511, 0, 511, 1, 205)  #图像大小是512*512  
reader.SetFileNameSliceOffset(0)
reader.SetFileNameSliceSpacing(1)
reader.SetDataSpacing(0.75, 0.75, 0.75)
reader.Update()
readerImageCast = vtk.vtkImageCast()
readerImageCast.SetInputConnection(reader.GetOutputPort())
readerImageCast.SetOutputScalarTypeToUnsignedShort()
readerImageCast.Update()

OutFile_Path = "C:\\Users\\chenjiaxing\\Desktop\\p4.vti"
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName(OutFile_Path);
writer.SetInputConnection(readerImageCast.GetOutputPort());
writer.Write();