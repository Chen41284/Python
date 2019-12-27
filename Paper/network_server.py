import socket


def getHostIp():
    name = socket.getfqdn(socket.gethostname(  ))
    #获取本机ip
    ip = socket.gethostbyname(name)
    return ip




if __name__ == '__main__':
    ip = getHostIp()
    print(ip)

