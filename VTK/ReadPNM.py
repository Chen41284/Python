#!/usr/bin/env python

"""
"""

import vtk


def main():
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\VTKTextBook\\Data\\Frog\\frogTissue.16"
    reader = vtk.vtkPNMReader()
    reader.SetFileName(fileName)

    imageViewer = vtk.vtkImageViewer2()
    imageViewer.SetInputConnection(reader.GetOutputPort())
    iren = vtk.vtkRenderWindowInteractor()
    imageViewer.SetupInteractor(iren)
    imageViewer.Render()
    imageViewer.GetRenderer().ResetCamera()
    imageViewer.Render()

    iren.Start()
    


if __name__ == '__main__':
    main()