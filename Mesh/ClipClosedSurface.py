import vtk

def ClipClosedSurface():
    colors = vtk.vtkNamedColors()
    # Create a sphere
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetThetaResolution(20)
    sphereSource.SetPhiResolution(11)
    sphereSource.Update()

    polyData = sphereSource.GetOutput()

    center = polyData.GetCenter()
    plane1 = vtk.vtkPlane()
    plane1.SetOrigin(center[0], center[1], center[2])
    plane1.SetNormal(0.0, -1.0, 0.0)
    plane2 = vtk.vtkPlane()
    plane2.SetOrigin(center[0], center[1], center[2])
    plane2.SetNormal(0.0, 0.0, 1.0)
    plane3 = vtk.vtkPlane()
    plane3.SetOrigin(center[0], center[1], center[2])
    plane3.SetNormal(-1.0, 0.0, 0.0)

    planes = vtk.vtkPlaneCollection()
    planes.AddItem(plane1)
    planes.AddItem(plane2)
    planes.AddItem(plane3)

    clipper = vtk.vtkClipClosedSurface()
    clipper.SetInputData(polyData)
    clipper.SetClippingPlanes(planes)
    # clipper.SetActivePlaneId(2)
    clipper.SetScalarModeToColors()
    clipper.SetClipColor(colors.GetColor3d("Green"))
    clipper.SetBaseColor(colors.GetColor3d("Red"))
    # clipper.SetActivePlaneColor(colors.GetColor3d("SandyBrown"))

    clipMapper = vtk.vtkDataSetMapper()
    clipMapper.SetInputConnection(clipper.GetOutputPort())

    clipActor = vtk.vtkActor()
    clipActor.SetMapper(clipMapper)
    clipActor.GetProperty().SetColor(1.0000, 0.3882, 0.2784)
    clipActor.GetProperty().SetInterpolationToFlat()

    # Create graphics stuff
    ren1 = vtk.vtkRenderer()
    ren1.SetBackground(colors.GetColor3d("SteelBlue"))

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(512, 512)
    renWin.SetWindowName("ClipClosedSurface")

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Add the actors to the renderer, set the background and size
    #
    ren1.AddActor(clipActor)

    # Generate an interesting view
    #
    ren1.ResetCamera()
    ren1.GetActiveCamera().Azimuth(120)
    ren1.GetActiveCamera().Elevation(30)
    ren1.GetActiveCamera().Dolly(1.0)
    ren1.ResetCameraClippingRange()

    renWin.Render()
    iren.Initialize()
    iren.Start()

if __name__ == "__main__":
    ClipClosedSurface()