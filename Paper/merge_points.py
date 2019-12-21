import vtk
import os
import re

def merge(feature_points_path, segment_points_path, merge_points_path):
    '''
    feature_points_path:str， 特征点的文件路径
    segment_points_path:str,  分割后网格的顶点的文件路径
    merge_points_path:str， 合并后的顶点存储路径
    '''
    # 读取feature_points
    vertice_number = 0
    feature_vertices = []
    with open(feature_points_path, 'r') as f1:
        for line in f1.readlines():
            line = str.split(line, ' ')
            vertice_number = vertice_number + 1
            feature_vertices.append([float(line[0]), float(line[1]), float(line[2])])
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(vertice_number)
    for i in range(vertice_number):
        points.SetPoint(i, feature_vertices[i])
    # 初始化合并的顶点集
    merge_points = vtk.vtkMergePoints()
    # merge_points.SetDataSet(points)
    merge_points.InitPointInsertion(points, points.GetBounds())
    id = vtk.reference(0)
    for i in range(vertice_number):
        merge_points.InsertUniquePoint(points.GetPoint(i), id)
    
    vertice_number = 0
    segment_points = []
    with open(segment_points_path, 'r') as f2:
        for line in f2.readlines():
            line = str.split(line, ' ')
            if line[0] == 'v':
                segment_points.append([float(line[1]), float(line[2]), float(line[3])])
                vertice_number = vertice_number + 1
            else:
                break
    id = vtk.reference(0)
    replated_points_id = []
    for i in range(vertice_number):
        inserted = merge_points.InsertUniquePoint(segment_points[i], id)
        if inserted == 0 :
            replated_points_id.append([id, i])
    
    result = merge_points.GetPoints()
    with open(merge_points_path, 'w') as f3:
        for i in range(result.GetNumberOfPoints()):
            pointTemp = result.GetPoint(i)
            f3.write("%f %f %f\n" % (pointTemp[0], pointTemp[1], pointTemp[2]))

    print("Replicated points number: %d" % len(replated_points_id))
    return len(replated_points_id)

def merge_single(feature_points_path, segment_points_dir):
    '''
    将每个分割的模块和特征点结合一个新的文件
    feature_points_path:str， 特征点文件的路径
    segment_points_dir:str, 分割后的文件所在的目录， pmesh文件的命名格式:xxx_Component0.pmesh  0为标识的id
    '''
    replated_number = 0
    for file in os.listdir(segment_points_dir):
        extension = os.path.splitext(file)[1]
        if extension == '.pmesh':
            pmesh = str.split(file, '_')[1]
            component = str.split(pmesh, '.')[0]
            feature_file = str.split(feature_points_path, '.')[0]
            merge_points_path = feature_file +  '_' + component + '.xyz'
            segment_points_path = segment_points_dir + file
            replated_number += merge(feature_points_path, segment_points_path, merge_points_path)
    
    print('-------------------------------------------------------')
    print('total replated number: %d' % replated_number)

def merge_series(feature_points_path, segment_points_dir):
    '''
    将分割后的模块按循序和特征点文件组合，生成一个序列的文件，表示重建逐步完善的过程
    feature_points_path:str， 特征点文件的路径
    segment_points_dir:str, 分割后的文件所在的目录， pmesh文件的命名格式:xxx_Component0.pmesh  0为标识的id
    '''
    replated_number = 0
    merge_points_file = str.split(feature_points_path, '.')[0] + '_Component'
    merge_points_path = merge_points_file
    for file in os.listdir(segment_points_dir):
        extension = os.path.splitext(file)[1]
        if extension == '.pmesh':
            if re.findall(r'.*_Component(\d+).*', feature_points_path) :
                merge_points_path = merge_points_file + re.findall(r'.*_Component(\d+).*', feature_points_path)[0]
            if re.findall(r'.*_Component(\d+).*', file) :
                merge_points_path = merge_points_path + re.findall(r'.*_Component(\d+).*', file)[0]
            merge_points_path = merge_points_path + '.xyz'
            segment_points_path = segment_points_dir + file
            replated_number += merge(feature_points_path, segment_points_path, merge_points_path)
            feature_points_path = merge_points_path

    print('-------------------------------------------------------')
    print('total replated number: %d' % replated_number)


if __name__=='__main__':
    feature_points_path = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\Armadillo4_LDsift.xyz"
    segment_points_dir = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Segment\\ProtBasedSeg\\Armadillo4\\"
    # merge_single(feature_points_path, segment_points_dir)
    merge_series(feature_points_path, segment_points_dir)