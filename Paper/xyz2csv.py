import vtk
import os
import numpy as np
import csv

def xyz2csv(xyz_file, csv_file = None):
    '''
    xyz_file:str
    '''
    vertices = np.genfromtxt(xyz_file).tolist()
    if csv_file is None:
        csv_file = xyz_file.replace(".xyz", ".csv")
    headers = ['x', 'y', 'z']

    with open(csv_file,'w', newline='')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(vertices)

if __name__=="__main__":
    # 测试数据流压缩
    xyz_path = "Data\\Armadillo4.xyz"
    
    xyz2csv(xyz_path)
