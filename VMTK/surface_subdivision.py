import os
import vmtk.vmtksurfacereader as sr
import vmtk.vmtksurfacesubdivision as ssdv
import vmtk.vmtksurfacewriter as sw

def surfacesubdivision(input_file, output_file):
    '''
    对网格表面进行细分
    '''
    surface_reader = sr.vmtkSurfaceReader()
    surface_reader.InputFileName = input_file
    surface_reader.Execute()

    surface_subdivision = ssdv.vmtkSurfaceSubdivision()
    surface_subdivision.NumberOfSubdivisions = 1
    surface_subdivision.Surface = surface_reader.Surface
    surface_subdivision.Method = "butterfly"
    surface_subdivision.Execute()

    surface_writer = sw.vmtkSurfaceWriter()
    surface_writer.OutputFileName = output_file
    surface_writer.Surface = surface_subdivision.Surface
    surface_writer.Execute()


if __name__ == '__main__':
    input_file = "id2_mode_sm_cl_center.vtp"
    output_file = "id2_mode_sm_cl_center_sbd.vtp"
    surfacesubdivision(input_file, output_file)