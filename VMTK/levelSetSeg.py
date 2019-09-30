import vmtk.vmtkimagereader as imagereader
import vmtk.vmtklevelsetsegmentation as levelsetseg
import vmtk.vmtkmarchingcubes as marchingcubes
import vmtk.vmtksurfacewriter as surfacewriter
def levelset_seg():
    '''
    图像的水平集分割，生成等值面
    '''
    input_file = "vesselVoi.vti"
    output_filename = 'vessellevelset.vtp'
    reader = imagereader.vmtkImageReader()
    # 图像序
    reader.InputFileName = input_file
    reader.Format = "vtkxml"
    reader.UseITKIO = 0
    reader.Execute()


    levelset = levelsetseg.vmtkLevelSetSegmentation()
    levelset.Image = reader.Image
    levelset.LevelSetsType = "geodesic"      # '["geodesic","curves","threshold","laplacian"]'
    levelset.FeatureImageType = "gradient"   # '["vtkgradient","gradient","upwind","fwhm"]'
    levelset.Execute()

    marchingcube = marchingcubes.vmtkMarchingCubes()
    marchingcube.Image = levelset.LevelSetsOutput
    marchingcube.Execute()


    writer = surfacewriter.vmtkSurfaceWriter()
    writer.Surface = marchingcube.Surface
    writer.Format = "vtkxml"
    writer.OutputFileName = output_filename
    writer.Execute()


if __name__ == '__main__':
    levelset_seg()