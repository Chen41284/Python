import socket



def getHostIp():
    name = socket.getfqdn(socket.gethostname())
    #获取本机ip
    ip = socket.gethostbyname(name)
    return ip

def socket_server():
    '''
    socket的服务端
    '''
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    server_ip = getHostIp()

    serverSocket.bind((server_ip ,12000))

    serverSocket.listen(1)


    print(server_ip)

    while True:
        connectionSocket, addr = serverSocket.accept()
        print("已与:",addr,"建立连接")
        for i in range(100):
            sendMessage = "数字" + str(i+1) + ";"
            if i % 10 == 0:
                sendMessage += "\n"
            connectionSocket.send(sendMessage.encode("utf-8"))

        connectionSocket.close()

        if addr is not None:
            break




if __name__ == '__main__':
    socket_server()

