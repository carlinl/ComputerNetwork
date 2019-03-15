# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from socket import *
import sys

hostname = '127.0.0.1'
serverPort = int(sys.argv[1])

print(f"\n IP address:{hostname}")
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

while True:
    #create a socket for connection
    connectionSocket,address = serverSocket.accept()
    try:
        request = connectionSocket.recv(1024).decode()
        #get the name of the file client wants
        request_file = request.split()[1]
        #open the file
        file = open(request_file[1:],'rb')
        content = file.read()
        #print(content)
        connectionSocket.send(b"HTTP/1.1 200 OK\r\n\r\n")
        connectionSocket.send(content)
        connectionSocket.close()
    except IOError:
        connectionSocket.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        connectionSocket.send(b"404 Not Found")
        connectionSocket.close()
