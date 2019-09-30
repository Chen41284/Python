import os
import vmtk.vmtksurfacereader as sr
import vmtk.vmtksurfaceclipper as sc
import vmtk.vmtksurfacewriter as sw
import vmtk.vmtkcenterlines as cl
import vmtk.vmtkendpointextractor as ep
import vmtk.vmtkbranchclipper as bc
import vmtk.vmtksurfaceconnectivity as sufct

def surfaceclipp(input_file, out_file):
    '''
    裁剪表面的端口,交互的方式
    '''
    surface_reader = sr.vmtkSurfaceReader()
    surface_reader.InputFileName = input_file
    surface_reader.Execute()

    surface_clipper = sc.vmtkSurfaceClipper()
    surface_clipper.Surface = surface_reader.Surface
    surface_clipper.Execute()

    surface_writer = sw.vmtkSurfaceWriter()
    surface_writer.Surface = surface_clipper.Surface
    surface_writer.OutputFileName = output_file
    surface_writer.Execute()

def surfaceclipp_centerline(input_file, output_file):
    '''
    使用中心线自动的裁剪端口
    '''
    surface_reader = sr.vmtkSurfaceReader()
    surface_reader.InputFileName = input_file
    surface_reader.Execute()

    centerline = cl.vmtkCenterlines()
    centerline.Surface = surface_reader.Surface
    centerline.Execute()

    endpointextractor = ep.vmtkEndpointExtractor()
    endpointextractor.Centerlines = centerline.Centerlines
    endpointextractor.Execute()

    branchclipper = bc.vmtkBranchClipper()
    branchclipper.Surface = surface_reader.Surface
    branchclipper.Centerlines = endpointextractor.Centerlines
    branchclipper.Execute()

    surface_connectivity = sufct.vmtkSurfaceConnectivity()
    surface_connectivity.Surface = branchclipper.Surface
    surface_connectivity.CleanOutput = 1
    surface_connectivity.Execute()

    surface_writer = sw.vmtkSurfaceWriter()
    surface_writer.Surface = surface_connectivity.Surface
    surface_writer.OutputFileName = output_file
    surface_writer.Execute()


if __name__ == '__main__':
    input_file = 'id2_mode_sm.vtp'
    output_file = 'id2_mode_sm_cl_center.vtp'
    surfaceclipp_centerline(input_file, output_file)