import socket
import os


#Diretorio base onde fica os arquivos
basedir = 'arquivos/'

#cria a conexão utilizando o protocolo UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 55555))
print('Servidor escutando')

while True:
    msgClientBytes, addressClient = server.recvfrom(1024) #recebe a mensagem do cliente e armazena tanto a mensagem como também o endereço
    msgClientString = msgClientBytes.decode() #decotifica a mensagem para string

    #print(f'arquivo escolhido pelo usuario: {msgClientString}')

    if msgClientString == "LIST":
        Arquivos = []
        with os.scandir(basedir) as arquivos:
            for arquivo in arquivos:
                Arquivos.append(str(arquivo))

        if not Arquivos:
            print("Sem arquivos na pasta")
            server.sendto("Pasta Vazia...".encode(), addressClient)
        else:
                server.sendto(str(Arquivos).encode(), addressClient)
                print(f"Enviado Lista de arquivos para: {addressClient}")
    else:
        try:
            with open(f'arquivos/{msgClientString}', 'rb') as file:
                for data in file:
                    server.sendto(data, addressClient)
                server.sendto(b'EOF', addressClient)
                print('arquivo enviado')
        except FileNotFoundError:
            server.sendto(b'ERRO: arquivo nao encontrado', addressClient)
