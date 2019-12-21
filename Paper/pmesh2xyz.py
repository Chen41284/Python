import os


def pmesh2xyz(pmesh_dirpath):
    '''
    将pmesh文件转为xyz文件，只存储顶点的三维坐标
    pmesh_path:str，pmesh文件所在的目录
    '''
    for file in os.listdir(pmesh_dirpath):
        extension = os.path.splitext(file)[1]
        if extension == '.pmesh':
            pmesh_vertices = []
            pmesh_file = pmesh_dirpath + file
            with open(pmesh_file, 'r') as fr:
                for line in fr.readlines():
                    line = str.split(line, ' ')
                    if line[0] == 'v':
                        pmesh_vertices.append([float(line[1]), float(line[2]), float(line[3])])

            xyz_path = pmesh_dirpath + os.path.splitext(file)[0] + '.xyz'
            with open(xyz_path, 'w') as fw:
                for i in range(len(pmesh_vertices)):
                    fw.write("%f %f %f\n" % (pmesh_vertices[i][0], pmesh_vertices[i][1], pmesh_vertices[i][2]))




if __name__=='__main__':
    pmesh_dirpath = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Segment\\ProtBasedSeg\\Armadillo4\\"
    pmesh2xyz(pmesh_dirpath)