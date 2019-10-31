import numpy as np
import point_and_seed as ps
import itertools   #内建模块，用于操作迭代器对象

def edge_detection(coeffs):
    """
    :param coeffs: 小波变化后获得的高低频信息
    coeffs = [aaa, (aad, ada, daa, add, dad, dda, ddd), (aad2, ada2, daa2, add2, dad2, dda2, ddd2)]

    """
    image_data = coeffs
    image_edge = roberts(image_data)
    return image_edge


def cal_gradient_roberts(image_data, operator, z, y, x):
    """
    用Roberts算子对每个体素计算梯度，用于边缘检测
    """
    operator_x = operator.operator_x
    operator_y = operator.operator_y
    operator_z = operator.operator_z
    super_point = image_data[z:(z + 2), y:(y + 2), x:(x + 2)]      #z, z + 1; y, y + 1; x, x + 1
    gx = np.sum(super_point * operator_x)  #默认d*f就是对应元素的乘积，multiply也是对应元素的乘积，dot（d,f）会转化为矩阵的乘积
    gy = np.sum(super_point * operator_y)
    gz = np.sum(super_point * operator_z)
    g = np.abs(gx) + np.abs(gy) + np.abs(gz)
    g = np.sqrt(gx ** 2 + gy ** 2 + gz ** 2)
    return g


def roberts(image_data):
    """
    3D-Roberts算子:
    """
    roberts_op = ps.roberts_operator()
    [lenZ, lenY, lenX] = image_data.shape
    image_edge = np.zeros((lenZ, lenY, lenX))
    # 扩展三维数据[lenZ, lenY, lenX]->[lenZ+1, lenY+1, lenX+1]
    image_new = np.zeros((lenZ + 1, lenY + 1, lenX + 1))
    image_new[0:lenZ, 0:lenY, 0:lenX] = image_data   #不包括lenz, lenY, lenX
    image_new[lenZ, 0:lenY, 0:lenX] = image_data[(lenZ - 1), :, :] 
    for k in range(lenZ):
        for j in range(lenY):
            for i in range(lenX):
                g = cal_gradient_roberts(image_new, roberts_op, k, j, i)
                image_edge[k, j, i] = g
    return image_edge


