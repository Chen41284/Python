import vtk

def main():
    fileName = "C:\\Users\\chenjiaxing\\Desktop\\VTKData\\Data\\vtk.png"
    readerFactory = vtk.vtkImageReader2Factory()
    reader = readerFactory.CreateImageReader2(fileName)
    reader.SetFileName(fileName)
    
    magnitude = vtk.vtkImageMagnitude()
    magnitude.SetInputConnection(reader.GetOutputPort())

    colors = vtk.vtkNamedColors()

    frequencies = vtk.vtkIntArray()

    histogram = vtk.vtkImageAccumulate()
    histogram.SetInputConnection(magnitude.GetOutputPort())
    histogram.SetComponentExtent(0, 255, 0, 0, 0, 0)
    histogram.SetComponentOrigin(0, 0, 0)
    histogram.SetComponentSpacing(1, 0, 0)
    histogram.IgnoreZeroOn()
    histogram.Update()

    numberOfTuples = 64
    frequencies.SetNumberOfComponents(1)
    frequencies.SetNumberOfTuples(numberOfTuples)
    output = histogram.GetOutput().GetScalarPointer()

    for j in range(numberOfTuples):
      frequencies.SetTuple(j, output)
      output = output + 1
    
    dataObject = vtk.vtkDataObject()
    dataObject.GetFieldData.AddArray(frequencies)

    barChart = vtk.vtkBarChartActor()
    barChart.SetInput(dataObject)
    barChart.SetTitle("Histogram")
    barChart.GetPositionCoordinate().SetValue(0.1,0.05,0.0)
    barChart.GetPosition2Coordinate().SetValue(0.95,0.85,0.0)
    barChart.GetProperty().SetColor(colors.GetColor3d("Banana").GetData())
    barChart.GetLegendActor().SetNumberOfEntries(
    dataObject.GetFieldData().GetArray(0).GetNumberOfTuples())
    barChart.LegendVisibilityOff()
    barChart.LabelVisibilityOff()
    
    count = 0
    for i in range(numberOfTuples):
      barChart.SetBarColor(count, colors.GetColor3d("Tomato").GetData())
    
    renderer = vtk.vtkRenderer()
    renderer.AddActor(barChart)
    renderer.SetBackground(colors.GetColor3d("Peacock").GetData())
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(640, 480)
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(renderWindow)
    
    renderWindow.Render()
    interactor.Initialize()
    interactor.Start()

if __name__ == '__main__':
    main()