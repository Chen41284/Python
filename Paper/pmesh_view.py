import vtk
import os
import random

def pmesh_view(dirpath, convert2ply = False, filetype = 'binary'):
    '''
    显示pmesh文件, pmesh为三角网格
    dirpath:文件的路径
    convert2ply:bool， 是否将pmesh文件转化为ply文件
    filetype:str, 'binary':转化为二进制文件， 'ascii':转化为文本文件
    '''
    colorsTable = [
        'antique_white', 'brown',  'forest_green', 'cadmium_lemon',
        'thistle', 'cyan', 'blue_medium', 'indigo',
        'magenta', 'olive', 'orange_red', 'grey'
        ]
    
    colors = vtk.vtkNamedColors()
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    vertice_total = 0
    face_total = 0
    colorIndex = 0
    for file in os.listdir(dirpath):
        file_path = os.path.join(dirpath, file)
        if os.path.splitext(file_path)[1] != '.pmesh':
            continue
        with open(file_path, 'r') as f:
            vertice_number = 0
            face_number = 0
            vertices = []
            faces = []
            for line in f.readlines():
                line = str.split(line, ' ')
                if (line[0] == 'v'):
                    vertice_number = vertice_number + 1
                    vertices.append([float(line[1]), float(line[2]), float(line[3])])
                elif (line[0] == 'p' and line[1] == '3'):
                    face_number = face_number + 1
                    # VTK中的顶点从0开始，pmesh中的顶点从1开始，所以减去1
                    faces.append([int(line[2]) - 1 , int(line[3]) - 1 , int(line[4]) - 1]) 
                else:
                    print("error")
            print("vertice number: %d, face number: %d" % (vertice_number, face_number))
            vertice_total = vertice_total + vertice_number
            face_total = face_total + face_number

            # 添加顶点
            points = vtk.vtkPoints()
            points.SetNumberOfPoints(vertice_number)
            for i in range(vertice_number):
                points.SetPoint(i, vertices[i])   
            
            # 添加面
            polys = vtk.vtkCellArray()
            for i in range(face_number):
                polys.InsertNextCell(3, faces[i])
            
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(polys)

            polyMapper = vtk.vtkPolyDataMapper()
            polyMapper.SetInputData(polydata)
            polyActor = vtk.vtkActor()
            polyActor.SetMapper(polyMapper)
            colorName = colorsTable[colorIndex]
            colorIndex = (colorIndex + 1) % len(colorsTable)
            polyActor.GetProperty().SetColor(colors.GetColor3d(colorName))

            renderer.AddActor(polyActor)

            if convert2ply :
                new_name = os.path.splitext(file_path)[0] + '.ply'
                ply_writer = vtk.vtkPLYWriter()
                ply_writer.SetInputData(polydata)
                ply_writer.SetFileName(new_name)
                if filetype.lower() == 'ascii':
                    ply_writer.SetFileTypeToASCII() 
                ply_writer.Write()

    print("------------------------------------------------------------------")
    print("vertice total: %d, face total: %d" % (vertice_total, face_total))

    renderer.SetBackground(colors.GetColor3d("MidnightBlue"))
    renderWindow.SetSize(512, 512)
    renderWindow.Render()
    renderWindowInteractor.Start()



if __name__=='__main__':
    dirpath = "C:\\Users\\chenjiaxing\\Desktop\\Segment\\ProtBasedSeg64\\Components\\Armadillo4"
    convert2ply = True
    pmesh_view(dirpath, convert2ply, 'ascii')