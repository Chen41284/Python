import vtk

class vtkIPWCallback(object):
    '''
    交互的回调
    完成实际工作：更新vtkPlane隐式函数。
    这反过来导致管道更新和裁剪对象。
    '''
    def __init__(self):
        self.Plane = 0
        self.Actor = 0
    
    def __call__(self, caller,event):
        planeWidget = caller
        rep = planeWidget.GetRepresentation()
        rep.GetPlane(self.Plane)


def implicitplane(filename):
    '''
    filename:str, 文件路径
    使用第二代ImplicitPlaneWidget2交互式定义多数据的剪切平面。 
    如果未指定任何参数，则vtkSphereSource会生成多边形数据。 
    通过指定.ply文件，该示例可以对任意多边形数据进行操作。
    '''
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetRadius(10.0)

    reader =  vtk.vtkPLYReader()

    # 设立一个渲染管道
    plane = vtk.vtkPlane()
    clipper = vtk.vtkClipPolyData()
    clipper.SetClipFunction(plane)
    clipper.InsideOutOn()
    if filename == None:
        clipper.SetInputConnection(sphereSource.GetOutputPort())
    else:
        reader.SetFileName(filename)
        clipper.SetInputConnection(reader.GetOutputPort())

    # 创建一个渲染的角色
    colors = vtk.vtkNamedColors()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(clipper.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    # actor.GetProperty().SetColor(colors.GetColor3d("black"))

    backFaces = vtk.vtkProperty()
    backFaces.SetDiffuseColor(.8, .8, .4)
    # backFaces.SetDiffuseColor(0, 0, 0)

    actor.SetBackfaceProperty(backFaces)

    # 渲染器和窗口
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderer.AddActor(actor)

    # 一个交互器
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderWindow.Render()

    # 回调将完成工作
    myCallback = vtkIPWCallback()
    myCallback.Plane = plane
    myCallback.Actor = actor

    rep = vtk.vtkImplicitPlaneRepresentation()
    rep.SetPlaceFactor(1.25) # 必须在放置小部件之前进行设置
    rep.PlaceWidget(actor.GetBounds())
    rep.SetNormal(plane.GetNormal())

    planeWidget = vtk.vtkImplicitPlaneWidget2()
    planeWidget.SetInteractor(renderWindowInteractor)
    planeWidget.SetRepresentation(rep)
    planeWidget.AddObserver('InteractionEvent', myCallback)

    # 渲染
    renderWindowInteractor.Initialize()
    renderWindow.Render()
    planeWidget.On()

    # 开启鼠标和键盘的交互模式
    renderWindowInteractor.Start()

if __name__=='__main__':
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\Python\\VTK\\VTKData\\Data\\bunny.ply"
    originfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Data\\Armadillo4.ply"
    reconfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Harris3D\\Armadillo4Harris_ScreenPoisson.ply"
    implicitplane(originfile)