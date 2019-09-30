#!/usr/bin/env python

"""
"""

import vtk


def main():
    colors = vtk.vtkNamedColors()

    fileName = 'C:/Users/chenjiaxing/Desktop/Python/vmtk/Spine_Neck.vti'

    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(fileName)
    reader.Update()
    cast = vtk.vtkImageCast()
    cast.SetInputData(reader.GetOutput())  
    cast.SetOutputScalarTypeToFloat()
    cast.SetOutputScalarTypeToUnsignedChar()
    cast.Update()
    #**********************************************************************
    rayCastFun = vtk.vtkPiecewiseFunction()
    #定义光线经过体数据后的颜色计算方式
    volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
    #光线投射法-最常用的体绘制方法
    volumeMapper.SetInputData(cast.GetOutput())
    #volumeMapper.SetVolumeRayCastFunction(rayCastFun)
    ##method 2

    #vtk.vtkGPUVolumeRayCastMapper> volumeMapperGpu = vtk.vtkGPUVolumeRayCastMapper()

    ##基于GPU加速的光线投射体绘制算法

    #volumeMapperGpu.SetInputData(cast.GetOutput())

    #volumeMapperGpu.SetImageSampleDistance(0.5)

    #volumeMapperGpu.SetSampleDistance(1.0)

    #volumeMapperGpu.SetAutoAdjustSampleDistances(1)

 

    #***********************************************************************

    volumeProperty = vtk.vtkVolumeProperty()#定义对象属性
    volumeProperty.SetInterpolationTypeToLinear()
    volumeProperty.ShadeOn()
    volumeProperty.SetAmbient(0.4)
    volumeProperty.SetDiffuse(0.6)
    volumeProperty.SetSpecular(0.2)
    compositeOpacity = vtk.vtkPiecewiseFunction()
    #Defines a piecewise function mapping.
    compositeOpacity.AddPoint(0, 0.00)
    compositeOpacity.AddPoint(216.19, 0.00)
    compositeOpacity.AddPoint(216.19, 0.851)
    compositeOpacity.AddPoint(256, 1)
    volumeProperty.SetScalarOpacity(compositeOpacity)
    color = vtk.vtkColorTransferFunction()
    color.AddRGBPoint(0, 0.231373, 0.298039, 0.7529)
    color.AddRGBPoint(210.8, 0.517, 0.654, 0.988)
    color.AddRGBPoint(256, 0.705, 0.0156, 0.149)
    volumeProperty.SetColor(color)
    volume = vtk.vtkVolume()
    #represents a volume(data & properties) in a rendered scene
    #volume.SetMapper(volumeMapperGpu)

    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)
    rendererVolume = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    rendererVolume.AddVolume(volume)
    renderWindow.AddRenderer(rendererVolume)
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()