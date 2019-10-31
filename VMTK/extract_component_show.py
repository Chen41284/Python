#!/usr/bin/env python

"""
"""

import vtk


def main():
    # Read the image
    fileName = 'C:\\Users\\chenjiaxing\\Pictures\\12.png'
    OutPut = 'C:\\Users\\chenjiaxing\\Pictures\\12R.png'
    readerFactory = vtk.vtkImageReader2Factory()
    reader = readerFactory.CreateImageReader2(fileName)
    reader.SetFileName(fileName)
    reader.Update()

    extractRedFilter = vtk.vtkImageExtractComponents()
    extractRedFilter.SetInputConnection(reader.GetOutputPort())
    extractRedFilter.SetComponents(0)
    extractRedFilter.Update()

    extractGreenFilter = vtk.vtkImageExtractComponents()
    extractGreenFilter.SetInputConnection(reader.GetOutputPort())
    extractGreenFilter.SetComponents(1)
    extractGreenFilter.Update()

    extractBlueFilter = vtk.vtkImageExtractComponents()
    extractBlueFilter.SetInputConnection(reader.GetOutputPort())
    extractBlueFilter.SetComponents(2)
    extractBlueFilter.Update()

    # Create actors
    inputActor = vtk.vtkImageActor()
    inputActor.GetMapper().SetInputConnection(reader.GetOutputPort())

    redActor = vtk.vtkImageActor()
    redActor.GetMapper().SetInputConnection(extractRedFilter.GetOutputPort())

    greenActor = vtk.vtkImageActor()
    greenActor.GetMapper().SetInputConnection(extractGreenFilter.GetOutputPort())

    blueActor = vtk.vtkImageActor()
    blueActor.GetMapper().SetInputConnection(extractBlueFilter.GetOutputPort())

    # Define viewport ranges
    # (xmin, ymin, xmax, ymax)
    inputViewport = [0.0, 0.0, 0.25, 1.0]
    redViewport = [0.25, 0.0, 0.5, 1.0]
    greenViewport = [0.5, 0.0, 0.75, 1.0]
    blueViewport = [0.75, 0.0, 1.0, 1.0]

    colors = vtk.vtkNamedColors()

    # Setup renderers
    inputRenderer = vtk.vtkRenderer()
    inputRenderer.SetViewport(inputViewport)
    inputRenderer.AddActor(inputActor)
    inputRenderer.ResetCamera()
    inputRenderer.SetBackground(colors.GetColor3d("Snow"))

    redRenderer = vtk.vtkRenderer()
    redRenderer.SetViewport(redViewport)
    redRenderer.AddActor(redActor)
    redRenderer.ResetCamera()
    redRenderer.SetBackground(colors.GetColor3d("Tomato"))

    greenRenderer = vtk.vtkRenderer()
    greenRenderer.SetViewport(greenViewport)
    greenRenderer.AddActor(greenActor)
    greenRenderer.ResetCamera()
    greenRenderer.SetBackground(colors.GetColor3d("Mint"))

    blueRenderer = vtk.vtkRenderer()
    blueRenderer.SetViewport(blueViewport)
    blueRenderer.AddActor(blueActor)
    blueRenderer.ResetCamera()
    blueRenderer.SetBackground(colors.GetColor3d("Peacock"))

    # Setup render window
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(1000, 250)
    renderWindow.AddRenderer(inputRenderer)
    renderWindow.AddRenderer(redRenderer)
    renderWindow.AddRenderer(greenRenderer)
    renderWindow.AddRenderer(blueRenderer)

    # Setup render window interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor() 
    style = vtk.vtkInteractorStyleImage()

    renderWindowInteractor.SetInteractorStyle(style)

    # Render and start interaction
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindow.Render()
    renderWindowInteractor.Initialize()

    renderWindowInteractor.Start()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(OutPut)
    writer.SetInputData(extractGreenFilter.GetOutput())
    writer.Write()


if __name__ == '__main__':
    main()