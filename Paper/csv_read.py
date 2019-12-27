import json
import os
import numpy as np
import os
import vtk
import pandas as pd
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

    

def csv_read(csv_file):
    '''
    csv_file:str
    '''
    data = pd.read_csv(csv_file, dtype = float)
    if (['x', 'y', 'z'] == data.columns).all():
        data_list = data.values.tolist()
        points_show(data_list)

if __name__=="__main__":
    # 测试数据流压缩
    csv_path = "Data\\Armadillo4.csv"
    
    csv_read(csv_path)