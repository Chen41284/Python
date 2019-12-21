#!/usr/bin/env python

import os.path

import vtk


def Decimation(filePath, reduction = 0.5):
    '''
    filePath:string, 文件的路径
    reduction:float, 减少的百分比 [0, 1]
    '''
    '''
    vtkDecimatePro的实现与最初在Proc Siggraph`92“三角网格抽取”中描述的算法类似，有三个主要区别。
    首先，该算法不一定保留网格的拓扑结构。
    其次，它保证提供用户指定的网格缩减因子（只要未设置某些约束-请参阅注意事项）。
    第三，它被设置为生成渐进网格，这是一个易于传输和增量更新的操作流
    '''
    '''
    VTK中的实现会保持网格的拓扑，可以简化的比例有限，有些最多只能简化72%
    低于简化上限的数值如0.5等，可以精确地实现相应的简化
    '''
    # Define colors
    colors = vtk.vtkNamedColors()
    backFaceColor = colors.GetColor3d("gold")
    inputActorColor = colors.GetColor3d("flesh")
    decimatedActorColor = colors.GetColor3d("flesh")
    colors.SetColor('leftBkg', [0.6, 0.5, 0.4, 1.0])
    colors.SetColor('rightBkg', [0.4, 0.5, 0.6, 1.0])

    if filePath and os.path.isfile(filePath):
        inputPolyData = ReadPolyData(filePath)
        if not inputPolyData:
            inputPolyData = GetSpherePD()
    else:
        inputPolyData = GetSpherePD()

    print("Before decimation")
    print(f"There are {inputPolyData.GetNumberOfPoints()} points.")
    print(f"There are {inputPolyData.GetNumberOfPolys()} polygons.")

    decimate = vtk.vtkDecimatePro()
    decimate.SetInputData(inputPolyData)
    decimate.SetTargetReduction(reduction)
    decimate.PreserveTopologyOn()
    decimate.Update()

    decimated = vtk.vtkPolyData()
    decimated.ShallowCopy(decimate.GetOutput())

    print("After decimation")
    print(f"There are {decimated.GetNumberOfPoints()} points.")
    print(f"There are {decimated.GetNumberOfPolys()} polygons.")
    print(f"Reduction: {(inputPolyData.GetNumberOfPolys() - decimated.GetNumberOfPolys()) / inputPolyData.GetNumberOfPolys()}")

    inputMapper = vtk.vtkPolyDataMapper()
    inputMapper.SetInputData(inputPolyData)

    backFace = vtk.vtkProperty()
    backFace.SetColor(backFaceColor)

    inputActor = vtk.vtkActor()
    inputActor.SetMapper(inputMapper)
    inputActor.GetProperty().SetInterpolationToFlat()
    inputActor.GetProperty().SetColor(inputActorColor)
    inputActor.SetBackfaceProperty(backFace)

    decimatedMapper = vtk.vtkPolyDataMapper()
    decimatedMapper.SetInputData(decimated)

    decimatedActor = vtk.vtkActor()
    decimatedActor.SetMapper(decimatedMapper)
    decimatedActor.GetProperty().SetColor(decimatedActorColor)
    decimatedActor.GetProperty().SetInterpolationToFlat()
    decimatedActor.SetBackfaceProperty(backFace)

    # There will be one render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(600, 300)

    # And one interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # Define viewport ranges
    # (xmin, ymin, xmax, ymax)
    leftViewport = [0.0, 0.0, 0.5, 1.0]
    rightViewport = [0.5, 0.0, 1.0, 1.0]

    # Setup both renderers
    leftRenderer = vtk.vtkRenderer()
    renderWindow.AddRenderer(leftRenderer)
    leftRenderer.SetViewport(leftViewport)
    leftRenderer.SetBackground((colors.GetColor3d('leftBkg')))

    rightRenderer = vtk.vtkRenderer()
    renderWindow.AddRenderer(rightRenderer)
    rightRenderer.SetViewport(rightViewport)
    rightRenderer.SetBackground((colors.GetColor3d('rightBkg')))

    # Add the sphere to the left and the cube to the right
    leftRenderer.AddActor(inputActor)
    rightRenderer.AddActor(decimatedActor)

    # Shared camera
    # Shared camera looking down the -y axis
    camera = vtk.vtkCamera()
    camera.SetPosition (0, -1, 0)
    camera.SetFocalPoint (0, 0, 0)
    camera.SetViewUp (0, 0, 1)
    camera.Elevation(30)
    camera.Azimuth(30)

    leftRenderer.SetActiveCamera(camera)
    rightRenderer.SetActiveCamera(camera)

    leftRenderer.ResetCamera()
    leftRenderer.ResetCameraClippingRange()

    renderWindow.Render()
    renderWindow.SetWindowName('Decimation')

    interactor.Start()


def ReadPolyData(file_name):
    import os
    extension = os.path.splitext(file_name)[1]
    extension = extension.lower()
    if extension == ".ply":
        reader = vtk.vtkPLYReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".vtp":
        reader = vtk.vtkXMLpoly_dataReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".obj":
        reader = vtk.vtkOBJReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".stl":
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".vtk":
        reader = vtk.vtkpoly_dataReader()
        reader.SetFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    elif extension == ".g":
        reader = vtk.vtkBYUReader()
        reader.SetGeometryFileName(file_name)
        reader.Update()
        poly_data = reader.GetOutput()
    else:
        # Return a None if the extension is unknown.
        poly_data = None
    return poly_data


def GetSpherePD():
    """
    :return: The PolyData representation of a sphere.
    """
    source = vtk.vtkSphereSource()
    source.SetThetaResolution(30)
    source.SetPhiResolution(15)
    source.Update()
    return source.GetOutput()


if __name__ == '__main__':
    originfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Data\\id2_model.ply"
    Decimation(originfile, 0.3)