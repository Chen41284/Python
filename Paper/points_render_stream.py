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

class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, points, filepath, interactor, vertice_number, actor):
        self.interactor = interactor
        self.points = points
        self.filepath = filepath
        self.vertice_number = vertice_number
        self.actor = actor
        self.interval = 10000
        self.Count = 0
        self.Update = True
        self.vertices = []
    
        # python代码没有重载C++中的虚函数，只能通过添加观察者的方法来子类化vtkInteractorStyle
        self.interactor.AddObserver("KeyPressEvent", self.OnKeyPress)
        # self.interactor.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        self.interactor.AddObserver("TimerEvent", self.printTime)

        self.readpoints()
    
    def OnKeyPress(self, obj, event):
        key = self.interactor.GetKeySym()
        if key == 'q':
            print('quit')
        elif key == 'e':
            print('exit')
        elif key == 'r':
            print('Reset Camera')
        elif key == 'F5':
            if self.Count < len(self.vertices):
                self.merge()
                print("Update")
            else:
                print("Not More data")
        else:
            print(key)
    
    def OnLeftButtonDown(self, obj, event):
        print("LeftButtonDown")

    # 打印当前时间
    def printTime(self, obj, event):
        print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
        if self.Count < len(self.vertices):
            self.merge()
            print("Update")
        elif self.Update:
            print("Update finish, no more data")
            self.Update = False
        else:
            pass
    
    # 读取文件中的顶点
    def readpoints(self):
        with open(self.filepath, 'r') as f:
            for line in f.readlines():
                line = str.split(line, ' ')
                self.vertices.append([float(line[0]), float(line[1]), float(line[2])])
        
        print(len(self.vertices))

    # 添加新的顶点
    def merge(self):
        merge_points = vtk.vtkMergePoints()
        merge_points.InitPointInsertion(self.points, self.points.GetBounds())
        id = vtk.reference(0)
        for i in range(self.vertice_number):
            merge_points.InsertUniquePoint(self.points.GetPoint(i), id)

        for i in range(self.Count, min(self.Count + self.interval, len(self.vertices))):
            inserted =  merge_points.InsertUniquePoint(self.vertices[i], id)
            if inserted == 1 :
                self.vertice_number += 1
        
        if self.Count + self.interval < len(self.vertices):
            self.Count = self.Count + self.interval
        else:
            self.Count = len(self.vertices)
        
        self.points = merge_points.GetPoints()
        self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.actor)
        self.actor = create_points_actor(self.points)
        self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.actor)
        self.interactor.GetRenderWindow().Render()
        self.interactor.GetRenderWindow().Render()

def points_reader(feature_points_path, steamfile):
    points = vtk.vtkPoints()
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

    points_render(points, steamfile, vertice_number)


def points_render(points, steamfile, vertice_number):
    colors = vtk.vtkNamedColors()
    actor = create_points_actor(points)
    # Create the widget
    textActor = vtk.vtkTextActor()
    textActor.SetInput("Refresh: Once every 5 seconds")
    textActor.GetTextProperty().SetColor( 0.0, 1.0, 0.0 )
    textWidget = vtk.vtkTextWidget()

    textRepresentation = vtk.vtkTextRepresentation()
    textRepresentation.GetPositionCoordinate().SetValue( .05, .05 )
    textRepresentation.GetPosition2Coordinate().SetValue( .1, .1 )
    textWidget.SetRepresentation( textRepresentation )

    # Create a renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor =  vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    textWidget.SetInteractor(renderWindowInteractor)
    textWidget.SetTextActor(textActor)
    textWidget.SelectableOff()
    textWidget.EnabledOn()

    style = KeyPressInteractorStyle(points, steamfile, renderWindowInteractor, vertice_number, actor)
    renderWindowInteractor.SetInteractorStyle(style)

    # Add the actor to the scene
    renderer.AddActor(actor)

    renderer.SetBackground(colors.GetColor3d("Green")) # Background color green

    # Render and interact
    renderWindow.Render()
    renderWindowInteractor.Initialize()
    renderWindowInteractor.CreateRepeatingTimer(5000)
    renderWindowInteractor.Start()


if __name__ == '__main__':
    feature_points_path = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\SIFT3D\\Armadillo4_LDsift.xyz"
    streamfile = "C:\\Users\\chenjiaxing\\Desktop\\paper-3D data\\Data\\Armadilo4.xyz"
    points_reader(feature_points_path, streamfile)