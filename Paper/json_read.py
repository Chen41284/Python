import json
import os
import numpy as np
import vtk

from points_render import create_points_actor, points_render


def points_show(vertices):
    '''
    vertices:array
    '''
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(vertices))
    for i in range(len(vertices)):
        points.SetPoint(i, vertices[i])
    
    points_render(points)


def json_decode(json_file):
    '''
    json_file:str, 文件的路径
    '''
    with open(json_file,'r') as f:
        data = json.load(f)
        print(data.keys())
    
    vertices = np.array(data['vertices'])

    points_show(vertices)
    


if __name__=='__main__':
    json_path = "Data\\Armadillo4_2.json"
    json_decode(json_path)


