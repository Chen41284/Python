import vtk



def cutter(filename):
    reader = vtk.vtkPLYReader()
    reader.SetFileName(filename)
    reader.Update()

    reader.GetOutput().GetPointData().SetActiveScalars("Intensity")

    plane = vtk.vtkPlane()
    bounds = [0] * 6
    reader.GetOutput().GetBounds(bounds)
    # origin = [(bounds[0] + bounds[1]) / 10, (bounds[2] + bounds[3]) / 10, (bounds[4] + bounds[5]) / 10] 
    # plane.SetOrigin(reader.GetOutput().GetCenter())
    # plane.SetOrigin(origin)
    plane.SetOrigin(0, 0, -30)
    plane.SetNormal(0, 0, 1)

    high = plane.EvaluateFunction([(bounds[1] + bounds[0]) / 2.0, (bounds[3] + bounds[2]) / 2.0, bounds[5] ])

    planeCut = vtk.vtkCutter()
    planeCut.SetInputConnection(reader.GetOutputPort())
    planeCut.SetCutFunction(plane)
    numberOfCuts = 10
    planeCut.GenerateValues(numberOfCuts, 0.99, 0.99 * high)

    # THIS GIVES THE 3D COORDINATES OF THE POINTS OF THE CUT PLANE
    # print(planeCut.GetOutput().GetPoints())
    # THIS GIVES THE DATA ASSOCIATED WITH EACH OF THE POINTS
    planeCut.GetOutput().GetPointData().GetAttribute(0)

    cutMapper = vtk.vtkPolyDataMapper()
    cutMapper.SetInputConnection(planeCut.GetOutputPort())

    cutActor = vtk.vtkActor()
    cutActor.SetMapper(cutMapper)

    # 渲染器和窗口
    colors = vtk.vtkNamedColors()
    renderer = vtk.vtkRenderer()
    renderer.AddActor(cutActor)
    renderer.SetBackground(colors.GetColor3d("MidnightBlue"))

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    # 交互器
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # 渲染一副图像（光照和相机自动创建）
    renderWindow.SetWindowName("OctreeVisualize")
    renderWindow.SetSize(600, 600)
    renderWindow.Render()

    # 开启鼠标和键盘的交互模式
    renderWindowInteractor.Start()

if __name__=='__main__':
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\Python\\VTK\\VTKData\\Data\\bunny.ply"
    originfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Data\\Armadillo4.ply"
    reconfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Harris3D\\Armadillo4Harris_ScreenPoisson.ply"
    cutter(originfile)