import vtk



def points_reader(points_file):
    points = vtk.vtkPoints()
    vertice_number = 0
    feature_vertices = []
    with open(points_file, 'r') as f1:
        for line in f1.readlines():
            line = str.split(line, ' ')
            vertice_number = vertice_number + 1
            feature_vertices.append([float(line[0]), float(line[1]), float(line[2])])
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(vertice_number)
    for i in range(vertice_number):
        points.SetPoint(i, feature_vertices[i])
    
    return points
    


def surface_recon_points(points):
    colors = vtk.vtkNamedColors()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    # Construct the surface and create isosurface.
    surf = vtk.vtkSurfaceReconstructionFilter()
    surf.SetInputData(polydata)

    cf = vtk.vtkContourFilter()
    cf.SetInputConnection(surf.GetOutputPort())
    cf.SetValue(0, 0.0)

    # Sometimes the contouring algorithm can create a volume whose gradient
    # vector and ordering of polygon (using the right hand rule) are
    # inconsistent. vtkReverseSense cures this problem.
    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()

    map = vtk.vtkPolyDataMapper()
    map.SetInputConnection(reverse.GetOutputPort())
    map.ScalarVisibilityOff()

    surfaceActor = vtk.vtkActor()
    surfaceActor.SetMapper(map)
    surfaceActor.GetProperty().SetDiffuseColor(colors.GetColor3d("Tomato"))
    surfaceActor.GetProperty().SetSpecularColor(colors.GetColor3d("Seashell"))
    surfaceActor.GetProperty().SetSpecular(.4)
    surfaceActor.GetProperty().SetSpecularPower(50)

    # Create the RenderWindow, Renderer and both Actors
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(640, 480)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)

    # Add the actors to the renderer, set the background and size
    renderer.AddActor(surfaceActor)
    renderer.SetBackground(colors.GetColor3d("Burlywood"))

    renderWindow.Render()
    interactor.Start()

if __name__ == '__main__':
    feature_points_path = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\Armadillo4_LDsift.xyz"
    streamfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Data\\Armadilo4.xyz"
    points = points_reader(streamfile)
    surface_recon_points(points)
