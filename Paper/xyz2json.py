import vtk
import codecs
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy
import json
import os


def points_reader(vertices_path):
    vertices = np.genfromtxt(vertices_path)
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(vertices))
    for i in range(len(vertices)):
        points.SetPoint(i, vertices[i])
    
    return points

def normals_compute(points, n = None, orientationPoint = None,  negate = False):
    """Generate point normals using PCA (principal component analysis).
    Basically this estimates a local tangent plane around each sample point p
    by considering a small neighborhood of points around p, and fitting a plane
    to the neighborhood (via PCA).

    :param int n: neighborhood size to calculate the normal
    :param list orientationPoint: adjust the +/- sign of the normals so that
        the normals all point towards a specified point. If None, perform a traversal
        of the point cloud and flip neighboring normals so that they are mutually consistent.

    :param bool negate: flip all normals
    """
    if n is not None:
        sampleSize = n

    else:
        sampleSize = points.GetNumberOfPoints() * .00005
        if sampleSize < 10:
            sampleSize = 10
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    print('Estimating normals using PCANormalEstimation')
    normals = vtk.vtkPCANormalEstimation()
    normals.SetInputData(polydata)
    normals.SetSampleSize(sampleSize)
    if orientationPoint is not None:
        normals.SetNormalOrientationToPoint()
        normals.SetOrientationPoint(orientationPoint)  
    else:
        normals.SetNormalOrientationToGraphTraversal()
    if negate:
        normals.FlipNormalsOn()
    normals.Update()

    points_array = vtk_to_numpy(points.GetData())
    normals_array = vtk_to_numpy(normals.GetOutput().GetPointData().GetNormals())

    return points_array, normals_array

def xyz2json(xyz_path, indent = False):
    '''
    xyz_path:str
    '''
    points = points_reader(xyz_path)
    # vertices, normals = normals_compute(points)
    vertices = vtk_to_numpy(points.GetData())
    name = os.path.basename(xyz_path).split('.')[0]
    points_dict = {
        "name": name, 
        "dataType" : "Points",
        "vertices_number" : len(vertices),
        "vertices" : vertices.tolist(),
        # "normals": normals.tolist()
    }


    json_path = xyz_path.split('.')[0] + '.json'
    if indent:
        json_str = json.dumps(points_dict, indent=4)
    else:
        json_str = json.dumps(points_dict)
    with open(json_path, 'w') as json_file:
        json_file.write(json_str)
    

if __name__=='__main__':
    xyz_path = "Data\\Armadillo4.xyz"
    xyz2json(xyz_path)
    

