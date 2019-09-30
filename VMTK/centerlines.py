import os
import vtk
import vmtk.vmtksurfacereader as sr
import vmtk.vmtkcenterlines as cl
import vmtk.vmtksurfaceviewer as sv
import vmtk.vmtkrenderer as rd


def centerlines():
    '''
    显示中心线
    '''
    input_file = "data\\levelSet\\vessellevelset_0.vtp"
    surfacereader = sr.vmtkSurfaceReader()
    surfacereader.InputFileName = input_file
    surfacereader.Execute()

    centerline = cl.vmtkCenterlines()
    centerline.Surface = surfacereader.Surface
    centerline.Execute()
    
    
    ''' centerline_mapper = vtk.vtkPolyDataMapper()
    centerline_mapper.SetInputData(centerline.Centerlines)
    centerline_actor = vtk.vtkActor()
    centerline_actor.SetMapper(centerline_mapper)

    centerline.vmtkRenderer.Renderer.AddActor(centerline_actor)
    surface_actor = centerline.vmtkRenderer.Renderer.GetActors().GetLastActor()
    surface_actor.GetProperty().SetOpacity(0)
    surface_actor.GetProperty().SetColor([0.1, 0.2, 0.5])
    centerline.vmtkRenderer.Render()'''

    surface_mapper = vtk.vtkPolyDataMapper()
    surface_mapper.SetInputData(surfacereader.Surface)
    surface_actor = vtk.vtkActor()
    surface_actor.SetMapper(surface_mapper)
    surface_actor.GetProperty().SetOpacity(0.3)
    color = [0.5, 0.6, 0.7]
    surface_actor.GetProperty().SetColor(color)


    renderer = rd.vmtkRenderer()
    renderer.Initialize()
    renderer.Renderer.AddActor(surface_actor)

    surfaceviewer = sv.vmtkSurfaceViewer()
    surfaceviewer.Surface = centerline.Centerlines
    # surfaceviwer.Surface = centerline.VoronoiDiagram
    surfaceviewer.Color = [0.5, 0.6, 0.7]
    surfaceviewer.ColorMap = "rainbow"  # "rainbow","blackbody","cooltowarm","grayscale"
    surfaceviewer.vmtkRenderer = renderer # centerline中vmtkrenderer在调用结束后，就回收内存了
    surfaceviewer.ArrayName = "MaximumInscribedSphereRadius" 
    surfaceviewer.Execute() 


if __name__ == '__main__':
    centerlines()