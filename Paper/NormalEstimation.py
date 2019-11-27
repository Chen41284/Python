import vtk
import codecs
from vtk.numpy_interface import dataset_adapter as dsa
from vtk.numpy_interface import algorithms as algs



def MakeGlyphs(src, size, glyph):
    # Source for the glyph filter
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(16)
    arrow.SetTipLength(.3)
    arrow.SetTipRadius(.1)

    glyph.SetSourceConnection(arrow.GetOutputPort())
    glyph.SetInputData(src)
    glyph.SetVectorModeToUseNormal()
    glyph.SetScaleModeToScaleByVector()
    glyph.SetScaleFactor(size)
    glyph.OrientOn()
    glyph.Update()


def npts_read_visual(filename, ply = None):
    '''
    读取npts文件中的顶点并显示它们的法线
    filename:string ，文件的路径
    '''
    with open(filename, 'r') as f:
        data = f.readlines()  # 将txt中所有字符串读入data
        total = len(data)
        
        points = vtk.vtkPoints()
        pointNormalsArray = vtk.vtkDoubleArray()
        pointNormalsArray.SetNumberOfComponents(3)
        pointNormalsArray.SetNumberOfTuples(total)

        index = 0
        for line in data:
            numbers = line.split()        # 将数据分隔
            points.InsertNextPoint(float(numbers[0]), float(numbers[1]), float(numbers[2]))
            pN = [float(numbers[3]), float(numbers[4]), float(numbers[5])]
            pointNormalsArray.SetTuple(index, pN)
            index = index + 1
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.GetPointData().SetNormals(pointNormalsArray)

        render(polydata, None, ply)



def normal_estimation_write(infile, outfile):
    '''
    infile:string, 输入的文件路径
    outfile:string,输出的文件路径
    '''
    reader = vtk.vtkSimplePointsReader()
    reader.SetFileName(infile)
    reader.Update()
    polyData = reader.GetOutput()
    
    sampleSize = polyData.GetNumberOfPoints() * .00005
    if sampleSize < 10:
        sampleSize = 10

    print('Estimating normals using PCANormalEstimation')
    normals = vtk.vtkPCANormalEstimation()
    normals.SetInputData(polyData)
    normals.SetSampleSize(sampleSize)
    normals.SetNormalOrientationToGraphTraversal()
    normals.FlipNormalsOn()
    normals.Update()

    output = normals.GetOutput()
    arr_normal = output.GetPointData().GetNormals()
    num = arr_normal.GetNumberOfTuples()

    f = codecs.open(outfile, "w")

    for index in range(num):
        for i in range(3):
            f.write("%.6f " % polyData.GetPoint(index)[i])
        for i in range(2):
            f.write("%.6f " % arr_normal.GetTuple(index)[i])
        f.write("%.6f\n" % arr_normal.GetTuple(index)[2])   

    f.close()


def normal_estimation_visual(filename, ply = None):
    '''
    filename:文件名
    顶点的法线评估
    '''
    reader = vtk.vtkSimplePointsReader()
    reader.SetFileName(filename)
    reader.Update()
    polyData = reader.GetOutput()

    sampleSize = polyData.GetNumberOfPoints() * .00005
    if sampleSize < 10:
        sampleSize = 10

    print('Estimating normals using PCANormalEstimation')
    normals = vtk.vtkPCANormalEstimation()
    normals.SetInputData(polyData)
    normals.SetSampleSize(sampleSize)
    normals.SetNormalOrientationToGraphTraversal()
    normals.FlipNormalsOff()
    normals.Update()

    render(normals.GetOutput(), None, ply)

def render(normals, points = None, ply = None):
    '''
     points:polydata
     normals:polydata
     ply: string
    '''

    colors = vtk.vtkNamedColors()
    radius = 1.0
    glyph3D = vtk.vtkGlyph3D()
    MakeGlyphs(normals, radius * .2, glyph3D)
    glyph3DMapper = vtk.vtkPolyDataMapper()
    glyph3DMapper.SetInputConnection(glyph3D.GetOutputPort())
    glyph3DActor = vtk.vtkActor()
    glyph3DActor.SetMapper(glyph3DMapper)
    glyph3DActor.GetProperty().SetDiffuseColor(colors.GetColor3d("red"))

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(colors.GetColor3d("SlateGray"))

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(640, 480)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # Add the actors to the renderer, set the background and size
    renderer.AddActor(glyph3DActor)

    # 显示模型
    if ply != None:
        plyData = vtk.vtkPLYReader()
        plyData.SetFileName(ply)
        plyData.Update()
        plyMapper = vtk.vtkPolyDataMapper()
        plyMapper.SetInputConnection(plyData.GetOutputPort())
        plyActor = vtk.vtkActor()
        plyActor.SetMapper(plyMapper)
        plyActor.GetProperty().SetDiffuseColor(colors.GetColor3d("blue"))
        renderer.AddActor(plyActor)

    # 显示原有的点
    if points != None:
        pointsMapper = vtk.vtkPolyDataMapper()
        pointsMapper.SetInputConnection(points.GetOutputPort())
        pointsActor = vtk.vtkActor()
        pointsActor.SetMapper(pointsMapper)
        pointsActor.GetProperty().SetDiffuseColor(colors.GetColor3d("green"))
        renderer.AddActor(pointsActor)

    # Generate an interesting view
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(120)
    renderer.GetActiveCamera().Elevation(30)
    renderer.GetActiveCamera().Dolly(1.0)
    renderer.ResetCameraClippingRange()

    renderWindow.Render()
    interactor.Initialize()
    interactor.Start()    
 

if __name__=='__main__':
    infile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\id2_mode.xyz"
    outfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\id2_mode.npts"
    plyfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\id2_model.ply"
    nptsfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\id2_mode_meshlab.xyz"
    normal_estimation_visual(infile, plyfile)
    # normal_estimation_write(infile, outfile)
    # npts_read_visual(nptsfile, plyfile)