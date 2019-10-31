#!/usr/bin/env python

"""
论文中图3的图片
"""

import vtk


def DicomMarchingCubes(fileName, isovalue, outputfile = None):
    '''
    fileName:str
    isovalue:int
    从Dicom图像的目录中创建等值面
    '''
    colors = vtk.vtkNamedColors()
    colors.SetColor("SkinColor", [255, 125, 64, 255])
    colors.SetColor("BkgColor", [51, 77, 102, 255])

    # 创建渲染相关的组件
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # 读取目录下面的DICOM图像
    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(fileName)
    reader.Update()

    
    # 等值面的提取
    Extractor = vtk.vtkMarchingCubes()
    Extractor.SetInputConnection(reader.GetOutputPort())
    Extractor.SetValue(0, 500)

    Stripper = vtk.vtkStripper()
    Stripper.SetInputConnection(Extractor.GetOutputPort())

    Mapper = vtk.vtkPolyDataMapper()
    Mapper.SetInputConnection(Stripper.GetOutputPort())
    Mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(Mapper)
    actor.GetProperty().SetDiffuseColor(colors.GetColor3d("SkinColor"))
    actor.GetProperty().SetSpecular(.3)
    actor.GetProperty().SetSpecularPower(20)
    actor.GetProperty().SetOpacity(1)


    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(reader.GetOutputPort())

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))

    # 设定相机的相关参数
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 0, -1)
    aCamera.SetPosition(0, -1, 0)
    aCamera.SetFocalPoint(0, 0, 0)
    aCamera.ComputeViewPlaneNormal()
    aCamera.Azimuth(30.0)
    aCamera.Elevation(30.0)

    # 将相关组件添加到渲染环境中
    aRenderer.AddActor(outline)
    aRenderer.AddActor(actor)
    aRenderer.SetActiveCamera(aCamera)
    aRenderer.ResetCamera()
    aCamera.Dolly(1.5)

    # 设定背景颜色
    aRenderer.SetBackground(colors.GetColor3d("BkgColor"))
    renWin.SetSize(640, 480)

    # 设定相机的裁剪
    # aRenderer.ResetCameraClippingRange()

    # 初始化窗口交互逻辑
    iren.Initialize()
    iren.Start()

    if outputfile != None:
        writer = vtk.vtkPLYWriter()
        writer.SetInputConnection(Extractor.GetOutputPort())
        writer.SetFileName(outputfile)
        writer.Write()


def get_program_parameters():
    import argparse
    description = 'The skin and bone is extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical2.cxx
    This example reads a volume dataset, extracts two isosurfaces that
     represent the skin and bone, and then displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\Python\\Data\\DICOM\\"
    outputPLY = "marchingcubes.ply"
    DicomMarchingCubes(fileName, 500, outputPLY)