#!/usr/bin/env python
import vtk
from time import strftime, localtime
import os


def create_points_actor(points):
    colors = vtk.vtkNamedColors()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    vertexGlyphFilter = vtk.vtkVertexGlyphFilter()
    vertexGlyphFilter.SetInputData(polydata)
    vertexGlyphFilter.Update()

    # Create a mapper and actor
    mapper =  vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(vertexGlyphFilter.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(1)
    actor.GetProperty().SetColor(colors.GetColor3d("Yellow"))

    return actor


class UpdateObserver(object):
    def __init__(self, points, dirpath, renderer):
        self.renderer = renderer
        self.points = points
        self.dir = dirpath
        self.files = []
    
    def __call__(self, caller, event):
        key = caller.GetKeySym()
        print("Pressed: %s" % key )

class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, points, dirpath, interactor, vertice_number, actor):
        self.interactor = interactor
        self.points = points
        self.dir = dirpath
        self.vertice_number = vertice_number
        self.actor = actor
        self.files = []
        self.Count = 0

        for file in os.listdir(dirpath):
            file = dirpath + file
            self.files.append(file)

        print(len(self.files))
        # python代码没有重载C++中的虚函数，只能通过添加观察者的方法来子类化vtkInteractorStyle
        self.interactor.AddObserver("KeyPressEvent", self.OnKeyPress)
        # self.interactor.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        self.interactor.AddObserver("TimerEvent", self.printTime)
    
    def OnKeyPress(self, obj, event):
        key = self.interactor.GetKeySym()
        if key == 'q':
            print('quit')
        elif key == 'e':
            print('exit')
        elif key == 'r':
            print('Reset Camera')
        elif key == 'F5':
            if self.Count < len(self.files):
                self.merge()
                print("Update")
            else:
                print("Not More data")
        elif key == "minus":
            size = self.actor.GetProperty().GetPointSize()
            size -= 1
            self.actor.GetProperty().SetPointSize(size)
            self.interactor.GetRenderWindow().Render()
        elif key == "plus":
            size = self.actor.GetProperty().GetPointSize()
            size += 1
            self.actor.GetProperty().SetPointSize(size)
            self.interactor.GetRenderWindow().Render()
        else:
            print(key)
    
    def OnLeftButtonDown(self, obj, event):
        print("LeftButtonDown")

    # 打印当前时间
    def printTime(self, obj, event):
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

    # 添加新的顶点
    def merge(self):
        merge_points = vtk.vtkMergePoints()
        merge_points.InitPointInsertion(self.points, self.points.GetBounds())
        id = vtk.reference(0)
        for i in range(self.vertice_number):
            merge_points.InsertUniquePoint(self.points.GetPoint(i), id)
        
        with open(self.files[self.Count], 'r') as f:
            for line in f.readlines():
                line = str.split(line, ' ')
                inserted =  merge_points.InsertUniquePoint([float(line[0]), float(line[1]), float(line[2])], id)
                if inserted == 1 :
                    self.vertice_number += 1
        
        self.points = merge_points.GetPoints()
        self.Count += 1
        self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.actor)
        self.actor = create_points_actor(self.points)
        self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.actor)
        self.interactor.GetRenderWindow().Render()

def points_reader(feature_points_path, dirpath):
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

    points_render(points, dirpath, vertice_number)


def points_render(points, dirpath = None, vertice_number = None):
    colors = vtk.vtkNamedColors()
    points_actor = create_points_actor(points)

    # Create a renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor =  vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)


    if dirpath is not None and vertice_number is not None:
        # Create the widget
        textActor = vtk.vtkTextActor()
        textActor.SetInput("KeyPress 'F5' to Refresh")
        textActor.GetTextProperty().SetColor( 0.0, 1.0, 0.0 )
        textWidget = vtk.vtkTextWidget()

        textRepresentation = vtk.vtkTextRepresentation()
        textRepresentation.GetPositionCoordinate().SetValue( .05, .05 )
        textRepresentation.GetPosition2Coordinate().SetValue( .1, .1 )
        textWidget.SetRepresentation( textRepresentation )
        textWidget.SetInteractor(renderWindowInteractor)
        textWidget.SetTextActor(textActor)
        textWidget.SelectableOff()
        textWidget.EnabledOn()

        # callback = UpdateObserver(points, dirpath, renderer)
        # renderWindowInteractor.AddObserver('KeyPressEvent', callback)

        style = KeyPressInteractorStyle(points, dirpath, renderWindowInteractor, vertice_number, points_actor)
        renderWindowInteractor.SetInteractorStyle(style)

    # Add the actor to the scene
    renderer.AddActor(points_actor)

    renderer.SetBackground(colors.GetColor3d("Green")) # Background color green

    # Render and interact
    renderWindow.Render()
    renderWindowInteractor.Initialize()
    renderWindowInteractor.CreateRepeatingTimer(5000)
    renderWindowInteractor.Start()


if __name__ == '__main__':
    feature_points_path = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\Armadillo4_LDsift.xyz"
    dirpath = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\xyz\\"
    points_reader(feature_points_path, dirpath)