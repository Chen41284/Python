# examples/Python/Basic/python_binding.py

import open3d as o3d
import numpy as np


def point_cloud(filepath):
    '''
    filepath:str, 文件的路径
    '''
    print("Load a ply point cloud, print it, and render it")
    pcd = o3d.io.read_point_cloud(filepath)
    print(pcd)
    print(np.asarray(pcd.points))
    #o3d.visualization.draw_geometries([pcd])

    # print("Downsample the point cloud with a voxel of 0.05")
    # downpcd = pcd.voxel_down_sample(voxel_size=0.10)
    # print(downpcd)
    #o3d.visualization.draw_geometries([downpcd])

    print("Recompute the normal of the downsampled point cloud")
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(
        radius = 100, max_nn= 10))
    pcd.orient_normals_towards_camera_location()
    pcd.orient_normals_to_align_with_direction()
    # o3d.visualization.draw_geometries([downpcd])
    print("Print the normal vectors of the first 10 points")
    print(np.asarray(pcd.normals)[0:10, :])
    print("")

    o3d.io.write_point_cloud("Armadillo4.xyzn", pcd)



if __name__ == "__main__":
    filepath = "Data\\Armadillo4.xyz"
    point_cloud(filepath)
