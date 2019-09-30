import os
import vmtk.vmtksurfacereader as sr
import vmtk.vmtkmeshgenerator as mg
import vmtk.vmtkmeshwriter as mw
import tetgen

def meshgenerate(input_file, output_file):
    '''
    从表面产生网格
    '''
    surface_reader = sr.vmtkSurfaceReader()
    surface_reader.InputFileName = input_file
    surface_reader.Execute()

    meshgenerator = mg.vmtkMeshGenerator()
    meshgenerator.Surface = surface_reader.Surface
    meshgenerator.TargetEdgeLength = 0.1
    meshgenerator.Execute()

    mesh_writer = mw.vmtkMeshWriter()
    mesh_writer.Mesh = meshgenerator.Mesh
    mesh_writer.OutputFileName = output_file
    mesh_writer.Execute()

if __name__ == '__main__':
    input_file = 'data2/id2_mode_sm_cl_center_cap.vtp'
    output_file = 'data2/id2_model.tec'
    meshgenerate(input_file, output_file)