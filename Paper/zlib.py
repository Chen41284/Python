import zlib
import requests

# zlib.compressobj 用来压缩数据流，用于文件传输
def file_compress(beginFile_path, zlibFile_path = None, level = 9):
    infile = open(beginFile_path, "rb")
    if zlibFile_path is None:
        zlibFile_path = beginFile_path + ".zlib"
    zfile = open(zlibFile_path, "wb")
    compressobj = zlib.compressobj(level)   # 压缩对象
    data = infile.read(1024)                # 1024为读取的size参数
    while data:
        zfile.write(compressobj.compress(data))     # 写入压缩数据
        data = infile.read(1024)        # 继续读取文件中的下一个size的内容
    zfile.write(compressobj.flush())    # compressobj.flush()包含剩余压缩输出的字节对象，将剩余的字节内容写入到目标文件中


def file_decompress(zlibFile_path, endFile_path = None):
    if zlibFile_path[-5:] != ".zlib":
        print("unsupported file type, the extension must be '.zlib' ")
        return
    zlibFile = open(zlibFile_path, "rb")
    if endFile_path is None:
        endFile_path = zlibFile_path[:-5]
    endFile = open(endFile_path, "wb")
    decompressobj = zlib.decompressobj()
    data = zlibFile.read(1024)
    while data:
        endFile.write(decompressobj.decompress(data))
        data = zlibFile.read(1024)
    endFile.write(decompressobj.flush())


if __name__=="__main__":
    # 测试数据流压缩
    beginFile_path = "Data\\Armadillo4.xyz"
    file_compress(beginFile_path)

    # 测试数据流解压
    zlibFile = "Data\\Armadillo4.xyz.zlib"
    file_decompress(zlibFile)
    
