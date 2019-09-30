import os
import vmtk.vmtksurfacereader as sr
import vmtk.vmtkflowextensions as fex 
import vmtk.vmtkcenterlines as cl
import vmtk.vmtksurfacewriter as sw

def suface_flow_extension(input_file, output_file):
    '''
    给表面添加流拓展
    '''

    surface_reader = sr.vmtkSurfaceReader()
    surface_reader.InputFileName = input_file
    surface_reader.Execute()

    centerline = cl.vmtkCenterlines()
    centerline.Surface = surface_reader.Surface
    centerline.SeedSelectorName = 'openprofiles'
    centerline.Execute()

    flow_extension = fex.vmtkFlowExtensions()
    flow_extension.Surface = surface_reader.Surface
    flow_extension.Centerlines = centerline.Centerlines
    flow_extension.AdaptiveExtensionLength = 1
    flow_extension.ExtensionRatio = 20
    flow_extension.CenterlineNormalEstimationDistanceRatio = 1
    flow_extension.Interactive = 0
    flow_extension.Execute()

    surface_writer = sw.vmtkSurfaceWriter()
    surface_writer.Surface = flow_extension.Surface
    surface_writer.OutputFileName = output_file
    surface_writer.Execute()


if __name__ == '__main__':
    input_file = 'id2_mode_sm_cl_center_sbd.vtp'
    output_file = 'ide2_model_sm_cl_center_sbd_ex.vtp'
    suface_flow_extension(input_file, output_file)