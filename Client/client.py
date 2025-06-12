import socket
import random

def recebe_com_perda(client, buffer_size, loss_rate=0.1):
    """
    Simula a perda de pacotes ao receber.
    loss_rate: probabilidade de perda (ex: 0.1 = 10%).
    """
    while True:
        msg, addr = client.recvfrom(buffer_size)
        if random.random() < loss_rate:
            print("** Pacote PERDIDO (simulado) **")
            continue  # ignora este pacote, simulando perda
        return msg, addr

def envia_ack_com_perda(client, ack_bytes, addr, loss_rate=0.1):
    """
    Simula a perda de ACKs ao enviar.
    """
    if random.random() < loss_rate:
        print(f"** ACK PERDIDO (simulado) para #{int.from_bytes(ack_bytes, 'big')} **")
        return  # não envia o ACK
    client.sendto(ack_bytes, addr)
    print(f"ACK #{int.from_bytes(ack_bytes, 'big')} enviado")


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

            print(f'dado recebido {msgReceivedBytes.decode()}')
            break

        case 2:
            msgClient = str(input("Qual arquivo gostaria de baixar? (arquivo.extensao): "))
            client.sendto(msgClient.encode(), ('localhost', 55555))

            pacotesRecebidos = {}
            with open('copia_' + msgClient, 'wb') as file:
                while True:
                    msgReceivedBytes, addressServer = client.recvfrom(2048)

                    if msgReceivedBytes == b'EOF':
                        print("Arquivo recebido com sucesso!")
                        break

                    if msgReceivedBytes.startswith(b'ERRO'):
                        print(msgReceivedBytes.decode())
                        break

                    numero_pacote = int.from_bytes(msgReceivedBytes[:4], byteorder='big')
                    dados_pacote = msgReceivedBytes[4:]

                    print(f'Pacote #{numero_pacote} recebido com {len(dados_pacote)} bytes')

                    pacotesRecebidos[numero_pacote] = dados_pacote

                    ack = numero_pacote.to_bytes(4, byteorder='big')
                    client.sendto(ack, addressServer)

                    print(f"ACK N: {numero_pacote} enviado")

                # Depois de receber todos os pacotes, escreve o arquivo na ordem correta
                for i in range(len(pacotesRecebidos)):
                    file.write(pacotesRecebidos[i])
            escolha = str(input('Arquivo recebido com sucesso, gostaria de baixar mais algum? (s/n): '))

            if escolha.lower() == "s":
                pass
            else:
                print("Obrigado, volte sempre!")
                break
