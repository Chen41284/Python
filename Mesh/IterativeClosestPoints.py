from __future__ import print_function

from xml.dom.minidom import parse
import xml.dom.minidom
import vtk
import numpy as np


def arrayFromVTKMatrix(vmatrix):
  """Return vtkMatrix4x4 or vtkMatrix3x3 elements as numpy array.
  The returned array is just a copy and so any modification in the array will not affect the input matrix.
  To set VTK matrix from a numpy array, use :py:meth:`vtkMatrixFromArray` or
  :py:meth:`updateVTKMatrixFromArray`.
  """
  from vtk import vtkMatrix4x4
  from vtk import vtkMatrix3x3
  import numpy as np
  if isinstance(vmatrix, vtkMatrix4x4):
    matrixSize = 4
  elif isinstance(vmatrix, vtkMatrix3x3):
    matrixSize = 3
  else:
    raise RuntimeError("Input must be vtk.vtkMatrix3x3 or vtk.vtkMatrix4x4")
  narray = np.eye(matrixSize)
  vmatrix.DeepCopy(narray.ravel(), vmatrix)
  return narray

def vtkMatrixFromArray(narray):
  """Create VTK matrix from a 3x3 or 4x4 numpy array.
  :param narray: input numpy array
  The returned matrix is just a copy and so any modification in the array will not affect the output matrix.
  To set numpy array from VTK matrix, use :py:meth:`arrayFromVTKMatrix`.
  """
  from vtk import vtkMatrix4x4
  from vtk import vtkMatrix3x3
  narrayshape = narray.shape
  if narrayshape == (4,4):
    vmatrix = vtkMatrix4x4()
    updateVTKMatrixFromArray(vmatrix, narray)
    return vmatrix
  elif narrayshape == (3,3):
    vmatrix = vtkMatrix3x3()
    updateVTKMatrixFromArray(vmatrix, narray)
    return vmatrix
  else:
    raise RuntimeError("Unsupported numpy array shape: "+str(narrayshape)+" expected (4,4)")

def updateVTKMatrixFromArray(vmatrix, narray):
  """Update VTK matrix values from a numpy array.
  :param vmatrix: VTK matrix (vtkMatrix4x4 or vtkMatrix3x3) that will be update
  :param narray: input numpy array
  To set numpy array from VTK matrix, use :py:meth:`arrayFromVTKMatrix`.
  """
  from vtk import vtkMatrix4x4
  from vtk import vtkMatrix3x3
  if isinstance(vmatrix, vtkMatrix4x4):
    matrixSize = 4
  elif isinstance(vmatrix, vtkMatrix3x3):
    matrixSize = 3
  else:
    raise RuntimeError("Output vmatrix must be vtk.vtkMatrix3x3 or vtk.vtkMatrix4x4")
  if narray.shape != (matrixSize, matrixSize):
    raise RuntimeError("Input narray size must match output vmatrix size ({0}x{0})".format(matrixSize))
  vmatrix.DeepCopy(narray.ravel())

def read_mps(mpspath : str):
    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(mpspath)
    collection = DOMTree.documentElement

    # 在集合中获取所有的配准点
    point_set = collection.getElementsByTagName("point")
    point_size = len(point_set)

    point_array = np.zeros(shape=(point_size, 3))

    # 打印每个配准点的详细信息
    for point in point_set:
        id = point.getElementsByTagName('id')[0]
        id_data = int(id.childNodes[0].data)
        x = point.getElementsByTagName('x')[0]
        x_data = float(x.childNodes[0].data)
        y = point.getElementsByTagName('y')[0]
        y_data = float(y.childNodes[0].data)
        z = point.getElementsByTagName('z')[0]
        z_data = float(z.childNodes[0].data)
        # print("id %d: %.2f, %.2f, %.2f" %(id_data, x_data, y_data, z_data))
        point_array[id_data] = [ x_data, y_data, z_data]
    
    np.set_printoptions(precision=3)
    # print(point_array)

    return point_array

def write_mps(mps_input : str, mps_output : str, array):
    # 使用minidom解析器打开 XML 文档
    DOMTree = xml.dom.minidom.parse(mps_input)
    collection = DOMTree.documentElement

    # 在集合中获取所有的配准点
    point_set = collection.getElementsByTagName("point")
    point_size = len(point_set)

    point_array = np.zeros(shape=(point_size, 3))

    # 打印每个配准点的详细信息
    for point in point_set:
        id = point.getElementsByTagName('id')[0]
        id_data = int(id.childNodes[0].data)
        x = point.getElementsByTagName('x')[0]
        y = point.getElementsByTagName('y')[0]
        z = point.getElementsByTagName('z')[0]

        x.childNodes[0].data = str(array[id_data][0])
        y.childNodes[0].data = str(array[id_data][1])
        z.childNodes[0].data = str(array[id_data][2])
    
    with open(mps_output, "w") as fh:
        DOMTree.writexml(fh)

def surface_clip(polydata, type : int):
    BoundingBox = polydata.GetBounds()

    center = [0] * 3
    normal = [0] * 3
    center[0] = (BoundingBox[0] + BoundingBox[1]) / 2
    center[1] = (BoundingBox[2] + BoundingBox[3]) / 2
    if (type == 0):  
        center[2] = BoundingBox[4] + 120
        normal[2] = -1
    else: 
        center[2] = BoundingBox[5] - 120
        normal[2] = 1

    plane1 = vtk.vtkPlane()
    plane1.SetOrigin(center[0], center[1], center[2])
    plane1.SetNormal(normal)
    planes = vtk.vtkPlaneCollection()
    planes.AddItem(plane1)

    clipper = vtk.vtkClipClosedSurface()
    clipper.SetInputData(polydata)
    clipper.SetClippingPlanes(planes)
    clipper.SetScalarModeToColors()
    clipper.SetActivePlaneId(0)
    clipper.Update()

    return clipper.GetOutput()


def IterativeClosestPoints(stlpath1 : str,  stlpath2 : str,  type : int):
    # ============ create source points ==============
    reader1 = vtk.vtkSTLReader()
    reader1.SetFileName(stlpath1)
    reader1.Update()

    # ============ 对模型进行裁剪，只保留配准点附近的网格 ==============
    source = surface_clip(reader1.GetOutput(), type)

    # ============ create target points ==============
    reader2 = vtk.vtkSTLReader()
    reader2.SetFileName(stlpath2)
    reader2.Update()

    # ============ 对模型进行裁剪，只保留配准点附近的网格 ==============
    target = surface_clip(reader2.GetOutput(), type)

    # ============ run ICP ==============
    icp = vtk.vtkIterativeClosestPointTransform()
    icp.SetSource(source)
    icp.SetTarget(target)
    # icp.GetLandmarkTransform().SetModeToRigidBody()
    # icp.GetLandmarkTransform().SetModeToSimilarity()
    icp.GetLandmarkTransform().SetModeToAffine()   # 当前实验发现仿射配准的效果最好
    # icp.DebugOn()
    icp.SetMaximumNumberOfIterations(1000)
    icp.StartByMatchingCentroidsOn()
    icp.Modified()
    icp.Update()

    icpTransformFilter = vtk.vtkTransformPolyDataFilter()
    icpTransformFilter.SetInputData(source)

    icpTransformFilter.SetTransform(icp)
    icpTransformFilter.Update()

    # ============ write the transformed stl ==============
    
    output_path = stlpath1[0:-4] + "transform3.stl"
    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(icpTransformFilter.GetOutputPort())
    writer.SetFileName(output_path)
    writer.SetFileTypeToBinary()
    writer.Write()
    

    matrix = icp.GetMatrix()
    # nparray = arrayFromVTKMatrix(matrix)

    return matrix

def nearest_neighbor(matrix, array, stlpath):
    reader1 = vtk.vtkSTLReader()
    reader1.SetFileName(stlpath)
    reader1.Update()

    target_polydata = reader1.GetOutput()

    # ============ create source points ==============
    print("Creating source points...")
    sourcePoints = vtk.vtkPoints()
    sourceVertices = vtk.vtkCellArray()

    for i in range(array.shape[0]):
        sp_id = sourcePoints.InsertNextPoint(array[i][0], array[i][1], array[i][2])
        sourceVertices.InsertNextCell(1)
        sourceVertices.InsertCellPoint(sp_id)

    source = vtk.vtkPolyData()
    source.SetPoints(sourcePoints)
    source.SetVerts(sourceVertices)

    trans = vtk.vtkTransform()
    trans.SetMatrix(matrix)

    icpTransformFilter = vtk.vtkTransformPolyDataFilter()
    icpTransformFilter.SetInputData(source)

    icpTransformFilter.SetTransform(trans)
    icpTransformFilter.Update()

    transformedSource = icpTransformFilter.GetOutput()

    my_cell_locator = vtk.vtkCellLocator()
    my_cell_locator.SetDataSet(target_polydata)  # reverse.GetOutput() --> vtkPolyData
    my_cell_locator.BuildLocator()

    # ============ display transformed points ==============
    pointCount = array.shape[0]
    transform_array = np.zeros(shape=(pointCount, 3))
    for index in range(pointCount):
        point = [0, 0, 0]
        transformedSource.GetPoint(index, point)
        # print("transformed source point[%s] = [%.2f, %.2f, %.2f]" % (index, point[0], point[1], point[2]))


        cellId = vtk.reference(0)
        c = [0.0, 0.0, 0.0]
        subId = vtk.reference(0)
        d = vtk.reference(0.0)
        my_cell_locator.FindClosestPoint(point,  c, cellId, subId, d)

        print("nearest neighbor point[%s] = [%.2f, %.2f, %.2f]" % (index, c[0], c[1], c[2]))
        transform_array[index] = c

    return transform_array



if __name__ == "__main__":
    stlpath1 = "STL/FemurLeft2.stl"           # 实验模型
    stlpath2 = "STL/FemurLeft7.stl"           # 标准模型
    mps_input = "FemoralRegistrationPoint.mps"
    mps_output = "FemoralRegistrationPoint2.mps"

    icpmatrix = IterativeClosestPoints(stlpath2, stlpath1, 0)  # 将标准模型平移旋转到和实验模型接近重合
    point_array = read_mps(mps_input)
    transform = nearest_neighbor(icpmatrix, point_array, stlpath1)
    write_mps(mps_input, mps_output, transform)