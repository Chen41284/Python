#!/usr/bin/env python
import vtk
from time import strftime, localtime
import os
import numpy as np

def create_points_actor(points):
    '''
    points:vtkPoints
    '''
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


def create_poly_actor(points, polys):
    '''
    points:vtkPoints
    polys:vtkCellArray
    '''
    colors = vtk.vtkNamedColors()
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    polydata.SetPolys(polys)
    # Create a mapper and actor
    mapper =  vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetPointSize(1)
    actor.GetProperty().SetColor(colors.GetColor3d("Yellow"))

    return actor

class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, points,  faces, interactor, points_actor, interval):
        '''
        points:vtkPoints
        faces:array
        interactor:vtkRenderWindowInteractor
        actor:vtkActor
        '''
        self.interactor = interactor
        self.points = points
        self.polys = vtk.vtkCellArray()
        self.points_actor = points_actor
        self.poly_actor = None
        self.interval = interval
        self.Count = 0
        self.Update = True
        self.faces = faces
    
        # python代码没有重载C++中的虚函数，只能通过添加观察者的方法来子类化vtkInteractorStyle
        self.interactor.AddObserver("KeyPressEvent", self.OnKeyPress)
        # self.interactor.AddObserver("LeftButtonPressEvent", self.OnLeftButtonDown)
        self.interactor.AddObserver("TimerEvent", self.TimeEvent)

    
    def OnKeyPress(self, obj, event):
        key = self.interactor.GetKeySym()
        if key == 'q':
            print('quit')
        elif key == 'e':
            print('exit')
        elif key == 'r':
            print('Reset Camera')
        elif key == 'F5':
            if self.Count < len(self.faces):
                self.AddFaces()
                print("Update")
            else:
                self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.points_actor)
                self.interactor.GetRenderWindow().Render()
                print("Not More data")
        else:
            print(key)
    
    def OnLeftButtonDown(self, obj, event):
        print("LeftButtonDown")

    # 打印当前时间
    def TimeEvent(self, obj, event):
        if self.Count < len(self.faces):
            self.AddFaces()
            print("Update: Add %d faces" % self.interval)
        elif self.Update:
            print("Update finish, no more data")
            self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.points_actor)
            self.interactor.GetRenderWindow().Render()
            self.Update = False
        else:
            pass

    # 添加新的顶点
    def AddFaces(self):
        for i in range(self.Count, min(self.Count + self.interval, len(self.faces))):
            self.polys.InsertNextCell(3, self.faces[i])
        
        if self.Count + self.interval < len(self.faces):
            self.Count = self.Count + self.interval
        else:
            self.Count = len(self.faces)

        if self.poly_actor != None:
            self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().RemoveActor(self.poly_actor)
        self.poly_actor = create_poly_actor(self.points, self.polys)
        self.interactor.GetRenderWindow().GetRenderers().GetFirstRenderer().AddActor(self.poly_actor)
        self.interactor.GetRenderWindow().Render()

def points_reader(vertices_path):
    vertices = np.genfromtxt(vertices_path)
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(len(vertices))
    for i in range(len(vertices)):
        points.SetPoint(i, vertices[i])
    
    return points

def faces_array(faces_path):
    array = np.genfromtxt(faces_path, dtype=int)
    return array[:,1:4] 


def poly_render(points, faces, fresh_time, interval):
    '''
    points:vtkPoints
    faces:array
    '''
    colors = vtk.vtkNamedColors()
    actor = create_points_actor(points)
    # Create the widget
    textActor = vtk.vtkTextActor()
    textActor.SetInput("Refresh: Once every second")
    textActor.GetTextProperty().SetColor( 0.0, 1.0, 0.0 )
    textWidget = vtk.vtkTextWidget()

    textRepresentation = vtk.vtkTextRepresentation()
    textRepresentation.GetPositionCoordinate().SetValue( .1, .1 )
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

    style = KeyPressInteractorStyle(points, faces , renderWindowInteractor, actor, interval)
    renderWindowInteractor.SetInteractorStyle(style)

    # Add the actor to the scene
    renderer.AddActor(actor)

    renderer.SetBackground(colors.GetColor3d("Green")) # Background color green

    # Render and interact
    renderWindow.Render()
    renderWindowInteractor.Initialize()
    renderWindowInteractor.CreateRepeatingTimer(fresh_time)
    renderWindowInteractor.Start()


if __name__ == '__main__':
    vertices_file = "Data\\Armadillo4.vertice"
    faces_file = "Data\\Armadillo4.faces"
    points = points_reader(vertices_file)
    faces = faces_array(faces_file)
    fresh_time = 1000                   # ms 毫秒
    interval = 5000                     # 每次更新增加的三角形数量
    poly_render(points, faces, fresh_time, interval)
