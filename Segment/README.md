# Segment
使用区域生长与边缘检测的分割代码


## start
算法的主流程

```Python
# 统计小波变化后的图像直方图
wavelet_hist(image_data)
# 提取种子点
seed_extract(dic)
# 执行的主体函数
start(file_dir, file_growing, file_edge):
    read = preprocess.read_dcm2array(file_dir)
    image_cw = preprocess.cw(read)
    coeffs = preprocess.wavelet3(image_cw)
    image_reduce = preprocess.wavelet_cw(coeffs[0])

    image_edge = edge.edge_detection(coeffs[0])
    volumerendering.show_edge(image_edge, file_edge)
   
    d = wavelet_hist(image_reduce)
    # # d = hist(image_cw)
    volume = []
    seed_tmp = seed_extract(d)
    grow_mark_all = np.zeros(image_reduce.shape)
    for i in range(len(seed_tmp)):
        seed_list_tmp = seed_tmp[i]
        # print seed_list_tmp.seed_zyx, seed_list_tmp.lower, seed_list_tmp.upper
        image_grow = seg.growing(image_reduce, seed_list_tmp,grow_mark_all)
        volume .append(volumerendering.show_growing(image_grow,i, file_growing))
    return volume
```


## preprocess
CT图像预处理
```Python
# 读入CT图像，转为numpy的数组
read_dcm2array(path_dcm)
# 调整窗宽和窗位
cw(image_data)
# 三维的小波变化
wavelet3(image_data)
# 小波后进行数据调整  将灰度值归一化到0~255
wavelet_cw(image_data)
# 平均值采样减少图像数据
image_reduce_dim(image_data)
```

## edge_detection
边缘检测的算法Roberts
```Python
# 对小波变换后的图像进行边缘检测
edge_detection(coeffs)
# 用Roberts算子对每个体素计算梯度，用于边缘检测
cal_gradient_roberts(image_data, operator, z, y, x)
# 3D-Roberts算子
roberts(image_data)
```

## point_and_seed
种子点
```Python
# 种子点的类
Seed
# 3D空间中点
Point
# roberts算子
roberts_operator
```

## seg_entropy
基于熵的分割算法
```Python
# 区域生长的主体函数
growing(image_data, seed, grow_mark_all)
# 计算超体素像素值
cal_avg(image_data, z, y, x)
```

## volumerendering
将分割后的数据保存，用于后续的体会渲染
```Python
# 将区域生长的数据进行保存
show_growing(image_data,index, file_growing)
# 将边缘检测的数据保存
show_edge(image_data, file_edge)
```