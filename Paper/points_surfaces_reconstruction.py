import vtk
import os
from time import strftime, localtime
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
from pypoisson import poisson_reconstruction


def create_mesh_actor(vertices, faces):
    '''
    vertices:array
    faces:array
    '''
    # 添加顶点
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(vertices))
    for i in range(len(vertices)):
        points.SetPoint(i, vertices[i])   
    
    # 添加面
    polys = vtk.vtkCellArray()
    for i in range(len(faces)):
        polys.InsertNextCell(3, faces[i])
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(polys)

    polyMapper = vtk.vtkPolyDataMapper()
    polyMapper.SetInputData(polydata)
    polyActor = vtk.vtkActor()
    polyActor.SetMapper(polyMapper)
    colors = vtk.vtkNamedColors()\
        
    polyActor.GetProperty().SetColor(colors.GetColor3d("White"))

    return polyActor


def create_points_actor(points):
    '''
    points:vtkPoints
    '''
    colors = vtk.vtkNamedColors()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
    vertexGlyphFilter.SetInputData(polydata)
    vertexGlyphFilter.Update()

    # Create a mapper and actor
    mapper =  vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(vertexGlyphFilter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(1)
    actor.GetProperty().SetColor(colors.GetColor3d("Yellow"))

    return actor

def create_surface_actor(points, n = None, orientationPoint = None,  negate = False):
    """Generate point normals using PCA (principal component analysis).
    Basically this estimates a local tangent plane around each sample point p
    by considering a small neighborhood of points around p, and fitting a plane
    to the neighborhood (via PCA).

    :param int n: neighborhood size to calculate the normal
    :param list orientationPoint: adjust the +/- sign of the normals so that
        the normals all point towards a specified point. If None, perform a traversal
        of the point cloud and flip neighboring normals so that they are mutually consistent.

    :param bool negate: flip all normals
    """

    if n is not None:
        sampleSize = n

    else:
        sampleSize = points.GetNumberOfPoints() * .00005
        if sampleSize < 10:
            sampleSize = 10
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    print('Estimating normals using PCANormalEstimation')
    normals = vtk.vtkPCANormalEstimation()
    normals.SetInputData(polydata)
    normals.SetSampleSize(sampleSize)
    if orientationPoint is not None:
        normals.SetNormalOrientationToPoint()
        normals.SetOrientationPoint(orientationPoint)  
    else:
        normals.SetNormalOrientationToGraphTraversal()
    if negate:
        normals.FlipNormalsOn()
    normals.Update()

    points_array = vtk_to_numpy(points.GetData())
    normals_array = vtk_to_numpy(normals.GetOutput().GetPointData().GetNormals())

    faces, vertices = poisson_reconstruction(points_array, normals_array, depth=10)

    return create_mesh_actor(vertices, faces)

class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, points, dirpath, interactor, vertice_number, points_actor, surface_actor):
        '''
        points:vtkPoints
        dirpath:str
        interactor:vtkRenderWindonInteractor
        vertice_number:int
        points_actor:vtkActor
        surface_actor:vtkActor
        '''
        self.interactor = interactor
        self.points = points
        self.dir = dirpath
        self.vertice_number = vertice_number
        self.points_actor = points_actor
        self.surface_actor = surface_actor
        self.files = []
        self.Update = True
        self.Count = 0

        for file in os.listdir(dirpath):
            file = dirpath + file
            self.files.append(file)

        print(len(self.files))
        # python代码没有重载C++中的虚函数，只能通过添加观察者的方法来子类化vtkInteractorStyle
        self.interactor.AddObserver("KeyPressEvent", self.OnKeyPress)
        # self.interactor.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        # self.interactor.AddObserver("TimerEvent", self.TimerEvent)
    
    def OnKeyPress(self, obj, event):
        key = self.interactor.GetKeySym()
        if key == 'q':
            print('quit')
        elif key == 'e':
            print('exit')
        elif key == 'r':
            print('Reset Camera')
        elif key == 'F5':
            if self.Count < len(self.files):
                self.merge()
                print("Update")
            else:
                print("Not More data")
        else:
            print(key)

    # 打印当前时间
    def TimerEvent(self, obj, event):
        if self.Count < len(self.files):
            self.merge()
            print("Update")
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
        elif self.Update:
            print("Update finish, no more data")
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
            self.Update = False
        else:
            pass

    # 添加新的顶点
    def merge(self):
        merge_points = vtk.vtkMergePoints()
        merge_points.InitPointInsertion(self.points, self.points.GetBounds())
        id = vtk.reference(0)
        for i in range(self.vertice_number):
            merge_points.InsertUniquePoint(self.points.GetPoint(i), id)
        
        with open(self.files[self.Count], 'r') as f:
            for line in f.readlines():
                line = str.split(line, ' ')
                inserted =  merge_points.InsertUniquePoint([float(line[0]), float(line[1]), float(line[2])], id)
                if inserted == 1 :
                    self.vertice_number += 1
        
        self.points = merge_points.GetPoints()
        self.Count += 1
        renderers = self.interactor.GetRenderWindow().GetRenderers()
        renderers.InitTraversal()
        points_renderer = renderers.GetNextItem()
        points_renderer.RemoveActor(self.points_actor)
        self.points_actor = create_points_actor(points)
        points_renderer.AddActor(self.points_actor)

        surface_renderer = renderers.GetNextItem()
        surface_renderer.RemoveActor(self.surface_actor)
        self.surface_actor = create_surface_actor(points)
        surface_renderer.AddActor(self.surface_actor)
        self.interactor.GetRenderWindow().Render()


def points_reader(vertices_path):
    vertices = np.genfromtxt(vertices_path)
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(vertices))
    for i in range(len(vertices)):
        points.SetPoint(i, vertices[i])
    
    return points, len(vertices)


def viewportBorder(renderer, last, color = None):
    '''
    renderer:vtkRenderer
    last:boool
    color:array [0] * 3
    '''
    # points start at upper right and proceed anti-clockwise
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(4)
    points.InsertPoint(0, 1, 1, 0)
    points.InsertPoint(1, 0, 1, 0)
    points.InsertPoint(2, 0, 0, 0)
    points.InsertPoint(3, 1, 0, 0)

    # create cells, and lines
    cells = vtk.vtkCellArray()
    cells.Initialize()

    lines = vtk.vtkPolyLine()

    # only draw last line if this is the last viewport
    # this prevents double vertical lines at right border
    # if different colors are used for each border, then do
    # not specify last
    if last :
        lines.GetPointIds().SetNumberOfIds(5)
    else :
        lines.GetPointIds().SetNumberOfIds(4)
    for i in range(4):
        lines.GetPointIds().SetId(i,i)
    if last:
        lines.GetPointIds().SetId(4, 0)

    cells.InsertNextCell(lines)

    # now make tge polydata and display it
    poly = vtk.vtkPolyData()
    poly.Initialize()
    poly.SetPoints(points)
    poly.SetLines(cells)

    # use normalized viewport coordinates since
    # they are independent of window size
    coordinate = vtk.vtkCoordinate()
    coordinate.SetCoordinateSystemToNormalizedViewport()

    mapper = vtk.vtkPolyDataMapper2D()
    mapper.SetInputData(poly)
    mapper.SetTransformCoordinate(coordinate)

    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)
    if color != None:
        actor.GetProperty().SetColor(color)
    else:
        actor.GetProperty().SetColor(vtk.vtkNamedColors().GetColor3d("SlateGray"))
    
    # line width should be at least 2 to be visible at extremes
    actor.GetProperty().SetLineWidth(4.0) # Line Width

    renderer.AddViewProp(actor)



def render(points, dirpath, vertice_number):
    colors = vtk.vtkNamedColors()
    points_actor = create_points_actor(points)
   

    # Create a renderer, render window, and interactor
    renWin = vtk.vtkRenderWindow()
    renderWindowInteractor =  vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renWin)
    surface_actor = create_surface_actor(points)


    style = KeyPressInteractorStyle(points, dirpath, renderWindowInteractor, 
                                      vertice_number, points_actor, surface_actor)
    renderWindowInteractor.SetInteractorStyle(style)


    textProperty = vtk.vtkTextProperty()
    textProperty.SetFontSize(16)
    textProperty.SetColor(0.3, 0.3, 0.3)

    # Add the actor to the scene
    # Create textActors
    points_textMapper = vtk.vtkTextMapper()
    points_textMapper.SetTextProperty(textProperty)
    points_textMapper.SetInput("Points\nKeyPress F5 to Update")

    points_textActor = vtk.vtkActor2D()
    points_textActor.SetMapper(points_textMapper)
    points_textActor.SetPosition(20, 20)

    points_renderer = vtk.vtkRenderer()
    points_renderer.AddActor(points_actor)
    points_renderer.AddActor(points_textActor)
    points_renderer.SetViewport(0, 0, 1.0 / 2.0, 1)
    points_renderer.SetBackground(colors.GetColor3d("Green"))
    viewportBorder(points_renderer, False)

    surface_textMapper = vtk.vtkTextMapper()
    surface_textMapper.SetTextProperty(textProperty)
    surface_textMapper.SetInput("Reconstruction suface")

    surface_textActor = vtk.vtkActor2D()
    surface_textActor.SetMapper(surface_textMapper)
    surface_textActor.SetPosition(20, 20)    

    surface_renderer = vtk.vtkRenderer()
    surface_renderer.AddActor(surface_actor)
    surface_renderer.AddActor(surface_textActor)
    surface_renderer.SetViewport(1.0 / 2.0, 0, 1, 1)
    surface_renderer.SetBackground(colors.GetColor3d("Green"))
    viewportBorder(surface_renderer, True)

    renWin.AddRenderer(points_renderer)
    renWin.SetSize(800, 600)
    renWin.AddRenderer(surface_renderer)



    # Render and interact
    renWin.Render()
    renderWindowInteractor.Initialize()
    renderWindowInteractor.CreateRepeatingTimer(5000)
    renderWindowInteractor.Start()


if __name__ == '__main__':
    feature_points_path = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\Armadillo4_LDsift.xyz"
    dirpath = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\xyz\\"
    points, vertice_number = points_reader(feature_points_path)
    render(points, dirpath, vertice_number)