import os
import pyvista as pv
import tetgen
import numpy as np

def tetgen_generator(input_file = None):
    '''
    生成网格
    '''
    if input_file == None:
        sphere = pv.Sphere()
        tet = tetgen.TetGen(sphere)
    else:
        tet = tetgen.TetGen(input_file)
    tet.tetrahedralize(order=1, mindihedral=20, minratio=1.5)
    grid = tet.grid
    grid.plot()


def tetgen_tetrahedralized(input_file = None):
    '''
    在xy平面下方提取球体四面体网格的一部分并绘制网格质量。
    '''
    if input_file == None:
        sphere = pv.Sphere()
        tet = tetgen.TetGen(sphere)
    else:
        object3D = pv.read(input_file)
        tet = tetgen.TetGen(object3D)
    tet.tetrahedralize(order=1, mindihedral=20, minratio=1.5)
    grid = tet.grid
    # get cell centroids
    cells = grid.cells.reshape(-1, 5)[:, 1:]
    cell_center = grid.points[cells].mean(1)

    # extract cells below the 0 xy plane
    # mask = cell_center[:, 2] < 0
    mask = cell_center[:,2] > 35
    cell_ind = mask.nonzero()[0]
    subgrid = grid.extract_cells(cell_ind)

    # advanced plotting
    plotter = pv.Plotter()
    plotter.set_background('w')
    plotter.add_mesh(subgrid, 'lightgrey', lighting=True)
    plotter.add_mesh(object3D, 'r', 'wireframe')
    plotter.add_legend([[' Input Mesh ', 'r'],
                        [' Tesselated Mesh ', 'black']])
    plotter.plot()

def tetgen_cell_quality(input_file):
    '''
    可以获得单元格质量并用其绘图
    '''
    if input_file == None:
        sphere = pv.Sphere()
        tet = tetgen.TetGen(sphere)
    else:
        object3D = pv.read(input_file)
        tet = tetgen.TetGen(object3D)
    tet.tetrahedralize(order=1, mindihedral=20, minratio=1.5)
    grid = tet.grid

    # get cell centroids
    cells = grid.cells.reshape(-1, 5)[:, 1:]
    cell_center = grid.points[cells].mean(1)

    # extract cells below the 0 xy plane
    mask = cell_center[:, 2] > 35
    cell_ind = mask.nonzero()[0]
    subgrid = grid.extract_cells(cell_ind)

    cell_qual = subgrid.quality

    # plot quality
    subgrid.plot(scalars=cell_qual, stitle='quality', cmap='bwr', flip_scalars=True)

if __name__ == '__main__':
    input_file = 'data2/id2_mode_sm_cl_center_cap.vtp'
    # tetgen_generator(input_file)
    tetgen_tetrahedralized(input_file)
    # tetgen_cell_quality(input_file)