import os
#对所有文件以数字递增的方式重命名
def file_rename():
    i = 0
    #需要重命名的文件绝对路径
    path = "C:/Users/chenjiaxing/Desktop/png/Spine_Muscle_Ext/"
    #读取该文件夹下所有的文件，排序
    filelist = sorted(os.listdir(path))   
    #遍历所有文件
    for files in filelist:   
        i = i + 1
        Olddir = os.path.join(path, files)    #原来的文件路径
        if os.path.isdir(Olddir):       #如果是文件夹则跳过
            continue
        #os.path.splitext(path)  #分割路径，返回路径名和文件扩展名的元组
        #文件名，此处没用到
        filename = os.path.splitext(files)[0]     
        #文件扩展名
        filetype = os.path.splitext(files)[1]         #如果你不想改变文件类型的话，使用原始扩展名
        Newdir = os.path.join(path, str(i)+filetype)   #新的文件路径
        os.rename(Olddir, Newdir)   
    return True

if __name__ == '__main__':
    file_rename()