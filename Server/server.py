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

    print(f'arquivo escolhido pelo usuario: {msgClientString}')

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
                data = file.read()
                
                print(f'Tamanho total dos dados: {len(data)} bytes')

                tamanho_pacote = 1024
                pacotes = []

                #a cada loop, pega um pedaço do arquivo com tamanho definido
                for i in range(0, len(data), tamanho_pacote):
                    pacotes.append(data[i:i+tamanho_pacote])

                print(f"Número de pacotes: {len(pacotes)}")

                if pacotes:
                    print(f"Tamanho do primeiro pacote: {len(pacotes[0])} bytes")
                    numero_pacote = 0
                    for item in pacotes:
                        # Converte o número do pacote para 4 bytes
                        seq_bytes = numero_pacote.to_bytes(4, byteorder='big')
                        mensagem = seq_bytes + item  # concatena o número com o pacote
                        server.sendto(mensagem, addressClient)
                        numero_pacote += 1

                    server.sendto(b'EOF', addressClient)
                else:
                    print("A lista de pacotes está vazia.")


               
        except FileNotFoundError:
            server.sendto(b'ERRO: arquivo nao encontrado', addressClient)
