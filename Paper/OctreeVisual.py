import vtk

class SliderObserver(object):
    def __init__(self, Octree, polyData, renderer):
        self.Octree = Octree
        self.level = 0
        self.polyData = polyData
        self.renderer = renderer
    
    def __call__(self, caller, event):
        self.level = vtk.vtkMath.Round(caller.GetRepresentation().GetValue())
        self.Octree.GenerateRepresentation(self.level, self.polyData)
        self.renderer.Render()

def OctreeVisualize(fileName):
    '''
    fileName:文件路径
    该函数显示PLY模型的空间八叉树划分
    '''
    # PLY模型的读取
    colors = vtk.vtkNamedColors()
    plyReader = vtk.vtkPLYReader()
    plyReader.SetFileName(fileName)
    plyMapper = vtk.vtkPolyDataMapper()
    plyMapper.SetInputConnection(plyReader.GetOutputPort())
    plyReader.Update()
    plyActor = vtk.vtkActor()
    plyActor.SetMapper(plyMapper)
    plyActor.GetProperty().SetInterpolationToFlat()
    plyActor.GetProperty().SetRepresentationToPoints()
    plyActor.GetProperty().SetColor(colors.GetColor3d("Yellow"))

    # 构建八叉树
    octree = vtk.vtkOctreePointLocator()
    octree.SetMaximumPointsPerRegion(5)
    octree.SetDataSet(plyReader.GetOutput())
    octree.BuildLocator()

    polydata = vtk.vtkPolyData()
    octree.GenerateRepresentation(0, polydata)

    octreeMapper = vtk.vtkPolyDataMapper()
    octreeMapper.SetInputData(polydata)

    octreeActor = vtk.vtkActor()
    octreeActor.SetMapper(octreeMapper)
    octreeActor.GetProperty().SetInterpolationToFlat()
    octreeActor.GetProperty().SetRepresentationToWireframe()
    octreeActor.GetProperty().SetColor(colors.GetColor3d("SpringGreen"))

    # 渲染器和窗口
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    # 交互器
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # 将模型加入场景中
    renderer.AddActor(plyActor)
    renderer.AddActor(octreeActor)
    renderer.SetBackground(colors.GetColor3d("MidnightBlue"))

    # 渲染一副图像（光照和相机自动创建）
    renderWindow.SetWindowName("OctreeVisualize")
    renderWindow.SetSize(600, 600)
    renderWindow.Render()

    # 创建设定八叉树划分细度的滑动条
    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(octree.GetLevel())
    sliderRep.SetValue(0)
    sliderRep.SetTitleText("Level")
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(.2, .2)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(.8, .2)
    sliderRep.SetSliderLength(0.075)
    sliderRep.SetSliderWidth(0.05)
    sliderRep.SetEndCapLength(0.05)
    sliderRep.GetTitleProperty().SetColor(colors.GetColor3d("Beige"))
    sliderRep.GetCapProperty().SetColor(colors.GetColor3d("MistyRose"))
    sliderRep.GetSliderProperty().SetColor(colors.GetColor3d("LightBlue"))
    sliderRep.GetSelectedProperty().SetColor(colors.GetColor3d("Violet"))

    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()
    sliderWidget.EnabledOn()

    # 给滑动条添加观察者
    callback = SliderObserver(octree, polydata, renderer)
    callback.Octree = octree
    callback.PolyData = polydata
    callback.Renderer = renderer

    sliderWidget.AddObserver('InteractionEvent', callback)

    renderWindowInteractor.Initialize()
    renderWindow.Render()

    renderWindowInteractor.Start()

if __name__=='__main__':
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\Harris3D-Cpp\\Armadillo4.ply"
    OctreeVisualize(fileName)