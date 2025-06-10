import socket
import os

UDP_IP = "127.0.0.1"  # Replace with the target IP address
UDP_PORT = 5005       # Replace with the target port

basepath = 'cli/'

#message = "Hello, UDP!"  # send the message via socket

with os.scandir(basepath) as arquivos:
    for arquivo in arquivos:
        with open(arquivo, 'r') as arq:
            conteudo = arq.read()
            print(conteudo)
            arq.close()

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
