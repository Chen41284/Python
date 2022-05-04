import vtk
import os
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


def transformSTL(inputstlPath : str, matrixPath : str, outputstlPath):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(inputstlPath)
    reader.Update()

    matrix = np.loadtxt(matrixPath)

    vtkmatrix = vtkMatrixFromArray(matrix)

    trans = vtk.vtkTransform()
    trans.SetMatrix(vtkmatrix)

    transfilter = vtk.vtkTransformFilter()
    transfilter.SetInputConnection(reader.GetOutputPort())
    transfilter.SetTransform(trans)

    writer = vtk.vtkSTLWriter()
    writer.SetInputConnection(transfilter.GetOutputPort())
    writer.SetFileName(outputstlPath)
    writer.Write()


def computeFemoralLandMarkMatrix(txtPath : str):
    '''
    计算将solidWorks中的假体平移和旋转到原点附近
    '''

    pSourcePoints = vtk.vtkPoints()
    pSourcePoints.InsertPoint(0, -73.292 ,  1.468 ,  -186.725)
    pSourcePoints.InsertPoint(1, -73.6702 ,  0.964468 ,  -171.738)
    pSourcePoints.InsertPoint(2, -73.292 ,  1.468 ,  -156.725)
    # pSourcePoints.InsertPoint(3, 57.6515, 29.5704 ,  -171.2451)
    # pSourcePoints.InsertPoint(4, 115.8690, 3.24210 ,  -160.804)

    pTargetPoints = vtk.vtkPoints()
    pTargetPoints.InsertPoint(0, -73.292 ,  1.468 ,  -186.725)
    pTargetPoints.InsertPoint(1, -73.292 ,  1.468 ,  -171.725)   
    pTargetPoints.InsertPoint(2, -73.292 ,  1.468 ,  -156.725)  # -y 横向的   后端切平面的法线
    # pTargetPoints.InsertPoint(3, -48.651500,  21.57049,  -208.7548)
    # pTargetPoints.InsertPoint(4, -106.8690,  -4.7579,  -219.1959)   # -z 轴向的   远端切平面的法线

    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks(pSourcePoints)
    landmarkTransform.SetTargetLandmarks(pTargetPoints)
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.Update()
 
    matrix = landmarkTransform.GetMatrix()

    nparray = arrayFromVTKMatrix(matrix)
    for i in range(4):
        for j in range(4):
            print("{:10.2f}".format(matrix.GetElement(i, j)) , end=", ")
        print("")
    
    np.set_printoptions(precision=3)
    np.savetxt(txtPath, nparray, fmt='%1.3f')



def computeTibiaTrayLandMarkMatrix(txtPath : str):
    '''
    计算将solidWorks中的假体平移和旋转到原点附近
    '''
    pSourcePoints = vtk.vtkPoints()
    pSourcePoints.InsertPoint(0, 0, 0, 0)
    pSourcePoints.InsertPoint(1, 0.5 , 0, 0)
    pSourcePoints.InsertPoint(2, 1.0,  0, 0)
    pSourcePoints.InsertPoint(3, 0, 0.5, 0)
    pSourcePoints.InsertPoint(4, 0, 1.0, 0)

    pTargetPoints = vtk.vtkPoints()
    pTargetPoints.InsertPoint(0, 0, 0, 0)
    pTargetPoints.InsertPoint(1, -0.5, 0, 0)   
    pTargetPoints.InsertPoint(2, -1.0, 0, 0)  
    pTargetPoints.InsertPoint(3, 0,  0.5,  0)
    pTargetPoints.InsertPoint(4, 0,  1.0,  0)   

    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks(pSourcePoints)
    landmarkTransform.SetTargetLandmarks(pTargetPoints)
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.Update()

    matrix = landmarkTransform.GetMatrix()

    nparray = arrayFromVTKMatrix(matrix)
    for i in range(4):
        for j in range(4):
            print("{:10.2f}".format(matrix.GetElement(i, j)) , end=", ")
        print("")
    
    np.set_printoptions(precision=3)
    np.savetxt(txtPath, nparray, fmt='%1.3f')


if __name__ == "__main__":
    # computeFemoralLandMarkMatrix("Data/TibiaTransform.txt")
    # transformSTL("Data/Tibia.stl", "Data/TibiaTransform.txt", "Data/TibiaASCII_t.stl")

    # computeTibiaTrayLandMarkMatrix("LandMarkMatrix/flip.txt")

    computeFemoralLandMarkMatrix("Data/fffff.txt")