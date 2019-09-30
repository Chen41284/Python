import os
import vmtk.vmtksurfacereader as sr
import vmtk.vmtksurfacecapper as sc
import vmtk.vmtksurfacewriter as sw

def surface_capper(input_file, output_file):
    '''
    将网格变得端口封住
    '''
    reader = sr.vmtkSurfaceReader()
    reader.InputFileName = input_file
    reader.Execute()

    capper = sc.vmtkSurfaceCapper()
    capper.Surface = reader.Surface
    capper.Execute()

    writer = sw.vmtkSurfaceWriter()
    writer.OutputFileName = output_file
    writer.Surface = capper.Surface
    writer.Mode = 'ascii'
    writer.Execute()


if __name__ == '__main__':
    input_file = 'data2/id2_mode_sm_cl_center.vtp'
    output_file = 'data2/id2_mode_sm_cl_center_cap.vtp'
    surface_capper(input_file, output_file)