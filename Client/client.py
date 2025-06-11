import socket
import threading
import json

while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("1- Listar")
    print("2- Baixar do Servidor")
    opt = int(input('digite um numero: '))

    match opt:
        case 1:
            client.sendto("LIST".encode(), ('localhost', 55555))
            msgReceivedBytes, addressServer = client.recvfrom(1024)

            if msgReceivedBytes == b'EOF':
                break

            if msgReceivedBytes.startswith(b'ERRO'):
                print(msgReceivedBytes.decode())
                break

            print(f'dado recebido {msgReceivedBytes}')
            break
        case 2:
            msgClient = str(input("Qual arquivo gostaria de baixar? (arquivo.extensao): "))
            client.sendto(msgClient.encode(), ('localhost', 55555))

            pacotesRecebidos = {}
            with open('copia_' + msgClient, 'wb') as file:
                while True:
                    msgReceivedBytes, addressServer = client.recvfrom(1000000)

                    if msgReceivedBytes == b'EOF':
                        break

                    if msgReceivedBytes.startswith(b'ERRO'):
                        print(msgReceivedBytes.decode())
                        break

                    numero_pacote = int.from_bytes(msgReceivedBytes[:4], byteorder='big')
                    dados_pacote = msgReceivedBytes[4:]

                    print(f'Pacote #{numero_pacote} recebido com {len(dados_pacote)} bytes')

                    pacotesRecebidos[numero_pacote] = dados_pacote

                # Depois de receber todos os pacotes, escreve o arquivo na ordem correta
                for i in range(len(pacotesRecebidos)):
                    file.write(pacotesRecebidos[i])
            escolha = str(input('Arquivo recebido com sucesso, gostaria de baixar mais algum? (s/n): '))

            if escolha == "s" or escolha == "S":
                pass
            elif escolha == "n" or escolha == "N":
                print("nao escolhido")
                break
