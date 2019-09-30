import os
import vmtk.vmtkmeshviewer as mv
import vmtk.vmtkmeshreader as mr

def meshview(input_file):
    '''
    显示网格
    '''
    mesh_reader = mr.vmtkMeshReader()
    mesh_reader.InputFileName = input_file
    mesh_reader.VolumeElementsOnly = 1
    mesh_reader.Execute()


    mesh_viewer = mv.vmtkMeshViewer()
    mesh_viewer.Mesh = mesh_reader.Mesh
    mesh_viewer.Representation = 'surface'
    mesh_viewer.Execute()

if __name__ == '__main__':
    input_file = 'data2/id2_model.neu'
    meshview(input_file)
