from pypoisson import poisson_reconstruction
from ply_from_array import points_normals_from, ply_from_array
import vtk


def create_points_actor(points):
    '''
    points:array
    '''
    vtk_points = vtk.vtkPoints()
    vtk_points.SetNumberOfPoints(len(points))
    for i in range(len(points)):
        vtk_points.SetPoint(i, points[i])
    
    colors = vtk.vtkNamedColors()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(vtk_points)

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
    colors = vtk.vtkNamedColors()
    polyActor.GetProperty().SetColor(colors.GetColor3d("White"))

    return polyActor


def render(points_actor, mesh_actor):
    '''
    points_actor:vtkActor
    mesh_actor:vtkActor
    '''
    colors = vtk.vtkNamedColors()

    points_renderer = vtk.vtkRenderer()
    points_renderer.AddActor(points_actor)
    points_renderer.SetViewport(0, 0, 1.0 / 2.0, 1)
    points_renderer.SetBackground(colors.GetColor3d("Green"))

    mesh_renderer = vtk.vtkRenderer()
    mesh_renderer.AddActor(mesh_actor)
    mesh_renderer.SetViewport(1.0 / 2.0, 0, 1, 1)
    mesh_renderer.SetBackground(colors.GetColor3d("Green"))

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(points_renderer)
    renWin.SetSize(800, 600)
    renWin.AddRenderer(mesh_renderer)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.Initialize()
    iren.Start()


def screenPoisson(xyz_file, ply_file = None):
    '''
    xyz_file:str， 文件的路径
    ply_file:str， 文件的路径
    '''

    # Helper Function to read the xyz-normals point cloud file
    points, normals = points_normals_from(xyz_file)

    faces, vertices = poisson_reconstruction(points, normals, depth=10)

    # 创建渲染的角色：点云，重建后的网格
    points_actor = create_points_actor(points)
    mesh_actor = create_mesh_actor(vertices, faces)

    render(points_actor, mesh_actor)

    # 将表面重建的网格保存为PLY文件
    if ply_file != None:
        ply_from_array(vertices, faces, output_file = ply_file)



if __name__ == '__main__':
    xyz_file = "Data\\Armadillo4_LDsift_meshlab.xyz"
    ply_file = "horse_reconstruction.ply"
    screenPoisson(xyz_file)