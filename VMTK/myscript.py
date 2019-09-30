from vmtk import pypes
from vmtk import vmtkscripts


#单幅图像序列的显示
SingleSlice = 'vmtkimagereader -ifile \"C:/Users/chenjiaxing/Desktop/5CD37D9A.dcm\" --pipe vmtkimageviewer'

#DICOM序列图像的显示
DicomSlice = 'vmtkimagereader -ifile \"C:/Users/chenjiaxing/Desktop/Python/vmtk/Spine_Bone.vti\" -useitk 0 --pipe vmtkimageviewer'

pngSlcie = 'vmtkimagereader -prefix \"C:/Users/chenjiaxing/Desktop/png/Spine_Bone/\" -useitk 0 -f "png" -pattern "%s%d.png" \
            -extent 0 512 0 512 1 188  --pipe vmtkimageviewer'
pngToMhd = 'vmtkimagereader -prefix \"C:/Users/chenjiaxing/Desktop/png/Spine_Muscle_Ext/\" -useitk 0 -f "png" -pattern "%s%d.png" \
            -extent 0 512 0 512 1 188  --pipe vmtkimagewriter -ofile \"C:/Users/chenjiaxing/Desktop/png/Spine_Muscle_Ext/Spine_head_40_400.mha\" '

VolumeExtraction = 'vmtkimagereader -ifile \"C:/Users/chenjiaxing/Desktop/Python/vmtk/Spine_Bone.vti\" --pipe \
                    vmtkimagevoiselector -ofile \"C:/Users/chenjiaxing/Desktop/Python/vmtk/Spine_Neck_Bone.vti\" '

#等值面绘， 效果和vtk一样
marchingCubes =  'vmtkimagereader -prefix \"C:/Users/chenjiaxing/Desktop/png/Spine_Bone/\" -useitk 0 -f "png" -pattern "%s%d.png" \
                  -extent 0 512 0 512 1 49   --pipe \
                 vmtkmarchingcubes -l 140 --pipe \
                 vmtkrenderer --pipe vmtkimageviewer --pipe vmtksurfaceviewer '
#core, 水平集
LevelSet = 'vmtklevelsetsegmentation -ifile Aorta_voi.mha  --pipe \
            vmtkrenderer --pipe  vmtksurfaceviewer'
LevelSet2 = 'vmtklevelsetsegmentation -ifile \"C:/Users/chenjiaxing/Desktop/Python/DICOM/0.dcm\" -ofile level_sets.vti'
LevelSet3 = 'vmtkmarchingcubes -ifile level_sets.vti -ofile model.vtp '
LevelSetWhole = 'vmtklevelsetsegmentation -ifile \"C:/Users/chenjiaxing/Desktop/Python/DICOM/0.dcm\" --pipe vmtkmarchingcubes -i @.o -ofile model2.vtp'

#core， 中心线
CenterLinesOut = 'vmtkcenterlines -ifile model3.vtp -ofile model3_centerlines.vtp'
CenterLines = 'vmtksurfacereader -ifile id2_model.vtp --pipe vmtkcenterlines  --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe \
               vmtksurfaceviewer -i @vmtkcenterlines.o -array MaximumInscribedSphereRadius'
CenterLineVor = 'vmtksurfacereader -ifile model3.vtp --pipe vmtkcenterlines --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe \
                 vmtksurfaceviewer -i @vmtkcenterlines.voronoidiagram -array MaximumInscribedSphereRadius \
                 --pipe vmtksurfaceviewer -i @vmtkcenterlines.o'


#core, 表面平滑
SmoothOut = 'vmtksurfacesmoothing -ifile model3.vtp -passband 0.1 -iterations 30 -ofile model3_sm.vtp'
surfaceSmooth = 'vmtksurfacereader -ifile model3.vtp --pipe vmtksurfacesmoothing -iterations 30 -passband 0.1 --pipe \
                 vmtkrenderer --pipe vmtksurfaceviewer -display 0 --pipe vmtksurfaceviewer -i @vmtksurfacereader.o -color 1 0 0 -display 1 '

#core, 打开表面的裁剪
ClipSurface = ' vmtksurfaceclipper -ifile model3_sm.vtp -ofile model3_sm_cl.vtp '
AutoClipSurface = 'vmtksurfacereader -ifile model3_sm.vtp --pipe vmtkcenterlines --pipe vmtkendpointextractor --pipe vmtkbranchclipper \
                   --pipe vmtksurfaceconnectivity -cleanoutput 1 --pipe vmtksurfacewriter -ofile model3_sm_ct.vtp'
#core,网格细化
Subdivision = 'vmtksurfacesubdivision -ifile id2_model.vtp -ofile id2_model_sm.vtp -method butterfly '

#core,添加流的拓展
FlowExtensions = ' vmtksurfacereader -ifile model3_sm_cl.vtp --pipe vmtkcenterlines -seedselector openprofiles --pipe \
                   vmtkflowextensions -adaptivelength 1 -extensionratio 20 -normalestimationratio 1 -interactive 0 --pipe  \
                   vmtksurfacewriter -ofile model3_sm_cl_ex.vtp'

#core,生成统一的元素网格 problem Tetgen(the wrapper was wrong)
Remeshing = 'vmtksurfaceremeshing -ifile id2_model.vtp -ofile id2_modelRe.vtp -edgelength 0.1'
surfaceToMesh = 'vmtksurfacetomesh -ifile id2_model.vtp -ofile id2_modelTM.vtu'
UniformMesh = 'vmtkmeshgenerator -ifile id1_model.vtp -ofile id2_modelTMGe.vtu -edgelengthfactor 0.1 -tetrahedralize 1'
UniformMeshView = 'vmtkmeshgenerator -ifile model3_sm_cl_sb_cp.vtp -edgelength 0.5 --pipe vmtkmeshviewer'
MeshGenTest = 'vmtkmeshgenerator -ifile id1_model.vtp -ofile id1_model.vtu -edgelength 0.5'

# 半径自适应网格
MeshTest2 = 'vmtksurfacereader -ifile id2_model.vtp --pipe vmtkcenterlines -endpoints 1  \
-seedselector openprofiles --pipe vmtkdistancetocenterlines -useradius 1 \
--pipe vmtkmeshgenerator -elementsizemode edgelengtharray -edgelengtharray \
DistanceToCenterlines -edgelengthfactor 0.3 -ofile id2_model.vtu'

#core,生成半径自适应元素网格 problem Tetgen(the wrapper was wrong) 封装的Tetfen执行错误
AdaptiveMesh = ' vmtksurfacereader -ifile model3_sm_cl.vtp --pipe vmtkcenterlines -endpoints 1 -seedselector openprofiles  \
                --pipe vmtkdistancetocenterlines -useradius 1 \
                --pipe vmtkmeshgenerator -elementsizemode edgelengtharray -edgelengtharray DistanceToCenterlines -edgelengthfactor 0.3 -ofile model3_sm_cl.vtu'

#core,封住端口
CappingSurface = 'vmtksurfacecapper -ifile model3_sm_cl_sb.vtp -ofile model3_sm_cl_sb_cp.vtp -interactive 0'

#core，将vtp转为stl
VTP2STL = 'vmtksurfacewriter -ifile model3_sm_cl_sb_cp.vtp -ofile model3_sm_cl_sb_cp.stl'

myPype = pypes.PypeRun(CenterLines)



