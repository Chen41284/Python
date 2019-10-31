import os
import vmtk.vmtksurfacesmoothing as ss
import vmtk.vmtksurfacereader as sr
import vmtk.vmtksurfacewriter as sw
import vmtk.vmtksurfaceviewer as sv
import vmtk.vmtkrenderer as rd
import vtk

def surface_smooth():
    '''
    网格表面的平滑
    '''
    input_file = 'id2_model.vtp'
    output_file = 'id2_mode_sm_laplace.vtp'
    surfacereader = sr.vmtkSurfaceReader()
    surfacereader.InputFileName = input_file
    surfacereader.Execute()

    # 没有平滑的网格表面
    originsurface_mapper = vtk.vtkPolyDataMapper()
    originsurface_mapper.SetInputData(surfacereader.Surface)
    originsurface_actor = vtk.vtkActor()
    originsurface_actor.SetMapper(originsurface_mapper)
    color = [0, 1, 0]
    originsurface_actor.GetProperty().SetColor(color)
    originsurface_actor.GetProperty().SetOpacity(0.8)

    surfacesmooth = ss.vmtkSurfaceSmoothing()
    surfacesmooth.Surface = surfacereader.Surface
    surfacesmooth.NumberOfIterations = 30
    surfacesmooth.PassBand = 1.0
    surfacesmooth.RelaxationFactor = 0.01
    surfacesmooth.BoundarySmoothing = 1
    surfacesmooth.NormalizeCoordinates = 1
    surfacesmooth.Method = "laplace"   # ["taubin","laplace"]
    surfacesmooth.Execute()

    renderer = rd.vmtkRenderer()
    renderer.Initialize()
    renderer.Renderer.AddActor(originsurface_actor)

    surface_viewer = sv.vmtkSurfaceViewer()
    surface_viewer.vmtkRenderer = renderer
    surface_viewer.Surface = surfacesmooth.Surface
    surface_viewer.Display = 1
    surface_viewer.Color = [1.0, 0, 0]
    surface_viewer.ColorMap = "cooltowarm"
    surface_viewer.Execute()

    surface_writer = sw.vmtkSurfaceWriter()
    surface_writer.OutputFileName = output_file
    surface_writer.Surface = surfacesmooth.Surface
    surface_writer.Execute()

    

if __name__ == '__main__':
    surface_smooth()