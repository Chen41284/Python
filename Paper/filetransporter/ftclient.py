#!/usr/bin/env python
# -*- coding:utf-8 -*-
#。——————————————————————————————————————————
#。
#。  ftclient.py
#。
#。 @Time    : 2018/7/26 00:09
#。 @Author  : ccapton
#。 @Software: PyCharm
#。 @Github  : https://github.com/ccapton
#。 @Email   : chenweibin1125@foxmail.com
#。__________________________________________
import sys
import socket
import threading
import argparse
import os,time

from list_file import FileFinder, FileFinder_Fast
from util import relative_path,dir_divider,checkfile,formated_size,formated_time,getFileMd5

python_version = sys.version
if python_version.startswith('2.'):
    python_version = '2'
elif python_version.startswith('3.'):
    python_version = '3'

divider_arg =  ' _*_ '
right_arrows = '>'*10
left_arrows = '<'*10

msg_index = 0

isCommandTConnected= False

default_data_socket_port = 9997
default_command_socket_port = 9998


COMMAND_CLOSE = '[COMMAND CLOSE]'
COMMANE_MISSION_SIZE = '[COMMAND MISSION_SIZE]'
COMMANE_FILE_INFO = '[COMMAND FILE_INFO]'

class Messenger:
    def __init__(self,socket):
        self.socket = socket
        self.send_debug = False
        self.recev_debug = False

    def send_msg(self,msg):
        if self.socket:
            try:
               self.socket.send(bytes(msg ,encoding='utf8'))
            except Exception as e:
                print(e)
                if self.send_debug:
                    print("连接错误")
        elif self.send_debug:
            print("Socket套接字为None")
        return self

    def recv_msg(self):
        if self.socket:
            try:
                msg = self.socket.recv(1024)
                return bytes(msg).decode('utf8')
            except Exception as e:
                print(e)
                if self.recev_debug:
                    print("连接错误")
        elif self.recev_debug:  
            print("Socket套接字为None")
        return None


class CommandThread(threading.Thread):
    def __init__(self, host=None, port=default_command_socket_port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.working = True
        self.messanger = None
        self.start_time = 0

    def setMissionSize(self,mission_size):
        self.mission_size = mission_size

    def setDataThread(self, server):
        self.dataThread = server

    def run(self):
        self.socket = socket.socket()
        try:
            self.socket.connect((self.host, self.port))
            global isCommandTConnected
            isCommandTConnected = True
            self.messanger = Messenger(self.socket)
            try:
                command = self.messanger.recv_msg()
                if self.working:
                   self.start_time = time.time()
                   print(command)
                self.messanger.send_msg(COMMANE_MISSION_SIZE + divider_arg + str(self.mission_size))

                while self.working and command and len(command) > 0:
                    if command.endswith('rootdir_create_ok'):
                        self.dataThread.waitingCreateDir = False
                    elif command.endswith('file_transport_ok') or command.endswith('dir_create_ok'):
                        self.dataThread.filefinder.recycle = False
                    elif command.endswith('file_existed'):
                        self.dataThread.filefinder.recycle = False
                        print('文件已存在：' + ' ' + command.split(divider_arg)[1])
                        if self.dataThread.findfileOver:
                            self.send_command(COMMAND_CLOSE)
                            self.socket.close()
                            self.working = False
                            print('完成任务耗时：' + '%s' % formated_time(time.time() - self.start_time))
                    elif command.endswith('ready'):
                        self.dataThread.send_filedata()
                    command = self.messanger.recv_msg()
                    if not self.working:
                        if sumsize == self.dataThread.sumsize:
                            print(right_arrows+'任务完成'+left_arrows)
                        self.socket.close()
            except ConnectionResetError as e:
                self.working = False
                if self.dataThread.filefinder:
                    self.dataThread.filefinder.finderCallback = None
                    self.dataThread.filefinder.recycle = True
                    self.dataThread.filefinder.off = True
                self.socket.close()
                self.dataThread.socket.close()
                print(right_arrows+'连接中断'+left_arrows)
                print(' %s...' % '请重新尝试此任务')
            except OSError as e:
                print('%s(%s)' % ('无法路由到主机',self.host))
            except Exception as e:
                print(e)
        except Exception:
            warning(right_arrows+'连接错误'+left_arrows)


    def send_fileinfo(self,fileinfo):
        if self.messanger:
            self.messanger.send_msg(fileinfo)

    def send_command(self,msg):
        if self.messanger:
            self.messanger.send_msg(msg)


class Client(threading.Thread , FileFinder.FinderCallback):
    def __init__(self,host,port):
        threading.Thread.__init__(self)
        self.filefinder = None
        self.host = host
        self.port = port
        self.singFile = True
        self.findfileOver = False
        self.sumsize = 0
        self.mission_read_size = 0
        self.waitingCreateDir = True
        self.once = True


    def setCommandThread(self, commandThread):
        self.commandThread = commandThread


    def setFilePath(self,filepath):
        self.filepath = filepath
        self.rootpath = filepath


    def onFindDir(self,dir_path):
        global msg_index
        msg_index += 1
        print('创建文件夹'+ os.path.basename(self.rootpath)+dir_divider()+relative_path(self.rootpath,dir_path))
        self.filename = dir_path
        self.filesize = -1
        self.commandThread.send_fileinfo(COMMANE_FILE_INFO + divider_arg
                                         +os.path.basename(self.rootpath) + dir_divider()+relative_path(self.rootpath,dir_path)+ divider_arg
                                         +str(-1)+divider_arg+
                                         str(msg_index))

    def onFindFile(self,file_path,size):
        global msg_index
        msg_index += 1
        print('文件 ：'+ os.path.basename(self.rootpath)+dir_divider()+relative_path(self.rootpath,file_path) +
              ' '+ formated_size(size))
        self.filename = file_path
        self.filesize = size
        if (os.path.isfile(file_path) and relative_path(self.rootpath,file_path) == ''):
            self.commandThread.send_fileinfo(COMMANE_FILE_INFO + divider_arg +
                                             os.path.basename(file_path) + divider_arg+
                                             str(size) + divider_arg+
                                             getFileMd5(file_path) + divider_arg+
                                             str(msg_index))
        else:
            self.commandThread.send_fileinfo(COMMANE_FILE_INFO + divider_arg +
                                             os.path.basename(self.rootpath) + dir_divider()+ relative_path(self.rootpath,file_path) + divider_arg+
                                             str(size) + divider_arg +
                                             getFileMd5(file_path) + divider_arg +
                                             str(msg_index))

    def run(self):
        if checkfile(self.filepath)[0] and checkfile(self.filepath)[1] == 1: # 文件
            self.singFile = True
            if self.connect_to_server():
                self.filefinder = FileFinder(self)
                self.filefinder.recycle = False
                self.filefinder.list_flie(self.filepath)
        elif checkfile(self.filepath)[0] and checkfile(self.filepath)[1] == 0: # 目录
            self.singFile = False
            self.findfileOver = False
            if self.connect_to_server():
                print('创建文件夹' + os.path.basename(self.filepath))
                self.commandThread.send_command(COMMANE_FILE_INFO + divider_arg+
                                                os.path.basename(self.filepath) + divider_arg +
                                                '-1' +divider_arg
                                                + str(msg_index))
                while self.waitingCreateDir:  #等待服务端（接收端的目录创建完成）
                    time.sleep(0.1)
                self.waitingCreateDir = True
                self.filefinder = FileFinder(self)
                self.filefinder.recycle = False
                self.filefinder.list_flie(self.filepath)  # 主体的循环，调用OnFindDir,OnFindFile
                self.findfileOver = True  # 结束传输
        elif not checkfile(self.filepath)[0]:
            print('请输入正确的文件路径')


    def connect_to_server(self):
        self.socket = socket.socket()
        try:
            self.socket.connect((self.host, self.port))
            print(bytes(self.socket.recv(1024)).decode(encoding='utf8'))
            print(right_arrows+'任务开始'+left_arrows)
            print('-'*30)
            return True
        except ConnectionError as e:
            print(e)
            if isCommandTConnected:
                print('%s %d' % ('服务端正在工作，但是数据套接字没有工作在端口上',self.port))
                print(right_arrows+'连接断开'+left_arrows)
                self.commandThread.messanger.send_msg(COMMAND_CLOSE)
                self.commandThread.socket.close()
                self.commandThread.working = False
            else:
                warning(right_arrows+'连接错误'+ left_arrows+
                  ' \n %s\n %s\n ' % ('请确认服务端是否正常运行','或者确认服务端的地址和端口号是否和您输入的一致')+
                  '%s ( %s , %d )' % ('您输入的主机和端口号是',self.host,self.port))
        except OSError as e:
            print('%s(%s)' % ('无法路由到主机',self.host))
        return False


    def send_filedata(self):
        readed_size = 0
        with open(self.filename,'rb') as f:
            filedata = f.read(4096)
            while len(filedata) > 0 :
                tempsize = len(filedata)
                readed_size += tempsize
                self.mission_read_size += tempsize
                try:
                   self.socket.send(filedata)
                   readed_show = '%s/%s' % (formated_size(readed_size),formated_size(self.filesize))
                   total_readed_show = '%s/%s' % (formated_size(self.mission_read_size),formated_size(sumsize))
                   current_filename = os.path.basename(self.filename) + ' '
                   sys.stdout.write(current_filename + readed_show + ' | %.2f%%  >>>%s %s | %.2f%%' %
                                    (float(readed_size / self.filesize * 100),
                                     '总计',
                                     total_readed_show,
                                     float(self.mission_read_size / sumsize * 100)) + '\r')
                except BrokenPipeError as e:
                    print(e)
                    if self.once:
                        if self.filefinder:
                            self.filefinder.finderCallback = None
                            self.filefinder.recycle = True
                            self.filefinder.off = True
                        print(right_arrows+'远端连接断开'+left_arrows)
                        self.once = False
                filedata = f.read(4096)
        print()
        if  readed_size == self.filesize and readed_size == 0:
            print(os.path.basename(self.filename) + ' %s' % '完成' )
        print('—'*30)
        if self.singFile:
            self.commandThread.send_command(COMMAND_CLOSE)
            self.socket.close()
            self.commandThread.working = False
            print('完成任务耗时：' + '%s' % formated_time(time.time() - self.commandThread.start_time))
        else:
            if self.findfileOver:
                self.commandThread.send_command(COMMAND_CLOSE)
                self.socket.close()
                self.commandThread.working = False
                print('完成任务耗时：'+'%s' % formated_time(time.time() - self.commandThread.start_time))


class MyfinderCallback(FileFinder_Fast.FinderCallback):
    def __init__(self):
        self.sumsize = 0
    def onFindDir(self,dir_path):
        pass
    def onFindFile(self,file_path,size):
        self.sumsize += size

def keyInPort():
    while True:
        temp_port = input('输入端口号： ')
        if int(temp_port) > 0 and int(temp_port) != default_command_socket_port:
            return (int(temp_port),True)
        elif int(temp_port) <= 0:
            warning('端口号必须为正整数')
        elif int(temp_port) == default_command_socket_port:
            warning('%s %d %s,%s' % ('端口','不可用',default_command_socket_port,'请输入其他的数字'))

def keyInFilePath():
    while True:
        filepath = input('请输入文件或者文件夹的路径：')
        if filepath.endswith(dir_divider()):
            filepath2 = filepath[:len(filepath)-1]
        else:
            filepath2 = filepath
        if checkfile(filepath2)[0]:
            return filepath2, True
        else:
            print('该路径下不存在任何东西')

def keyInHost():
    while True:
        host = input('请输入目标主机：')
        if len(host) > 0:
            return host, True

def warning(text):
    print('[%s] ' % '警告'+text)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath', required=False, help=('将要发送的文件(夹)路径'))
    parser.add_argument('-p', '--port', required=False, help=('程序传输数据的端口号'),type = int)
    parser.add_argument('-i', '--host', required=False, help=('将要发送的目的主机'),type = str)

    args = parser.parse_args()

    port = default_data_socket_port

    filepath_ok = True
    port_ok = True
    host_ok = False
    if args.port and args.port > 0 :
        port = args.port
        if port == default_command_socket_port:
            warning('%s %d %s,%s' % ('端口',default_command_socket_port,'不可用','请输入其他的数字'))
            port , port_ok = keyInPort()
    elif args.port and args.port <=0:
        warning('端口号必须为正整数')
        port, port_ok = keyInPort()

    filepath = args.filepath
    if not filepath:
        filepath , filepath_ok = keyInFilePath()
    elif not checkfile(args.filepath)[0]:
        warning('该路径下不存在任何文件')
        filepath , filepath_ok = keyInFilePath()

    host = args.host
    if not host:
        host , host_ok = keyInHost()
    else:
        host_ok = True

    if port_ok and filepath_ok and host_ok:
        findercallback = MyfinderCallback()
        if not checkfile(filepath)[1]:
           print('%s %s' % ('在此查找文件：',filepath))
        FileFinder_Fast(findercallback).list_flie(filepath)
        global sumsize
        sumsize = findercallback.sumsize
        file_type = ''
        if checkfile(filepath)[1]:
            file_type = '文件 ：'
        else:
            file_type = '文件夹（包括在内的所有文件）:'
        warning('%s %s' % ('您准备发送的是',file_type))
        print(filepath + ' | %s%s : %s' % ('总计','大小',formated_size(sumsize)))

        confirm = input('%s(Y/N):'% '继续发送？ ')
        while True:
            if confirm == 'y' or confirm == 'Y' or confirm == 'Yes'.upper() or confirm == 'yes'.lower():
                commandThread = None
                client = Client(host, port)
                commandThread = CommandThread(host)
                commandThread.setDataThread(client)
                commandThread.setMissionSize(sumsize)
                client.setCommandThread(commandThread)
                client.setFilePath(filepath)
                client.start()
                commandThread.start()
                break
            elif confirm == 'n' or confirm == 'N' or confirm == 'No'.upper() or confirm == 'no'.lower():
                warning('放弃任务...继续')
                break
            confirm = input('%s(Y/N):' % '继续发送？ ')

