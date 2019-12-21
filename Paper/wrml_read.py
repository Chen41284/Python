import vtk

def vrml_read(filename):
    '''
    读取并显示vrml格式的文件
    filename:文件的路径
    '''
    colors = vtk.vtkNamedColors()
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()

    importer = vtk.vtkVRMLImporter()
    importer.SetFileName(filename)
    importer.SetRenderWindow(renderWindow)
    importer.Update()

    actors = renderer.GetActors()
    print("There are %d actors" % actors.GetNumberOfItems())

    renderer.SetBackground(colors.GetColor3d("Burlwood"))
    renderWindow.SetSize(512, 512)
    renderWindow.Render()
    renderWindowInteractor.Start()

if __name__=='__main__':
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\Segment\\ProtBasedSeg64\PARTS\\armadillo.wrl"
    vrml_read(fileName) 