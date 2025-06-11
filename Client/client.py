import socket


while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("1- Listar")
    print("2- Baixar do Servidor")
    opt = int(input('digite um numero: '))

    match opt:
        case 1:
            client.sendto("LIST".encode(), ('localhost', 55555))
            msgReceivedBytes, addressServer = client.recvfrom(10000000)

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
            with open('copia_' + msgClient, 'wb') as file:
                while True:
                    msgReceivedBytes, addressServer = client.recvfrom(10000000)

                    if msgReceivedBytes == b'EOF':
                        break

                    if msgReceivedBytes.startswith(b'ERRO'):
                        print(msgReceivedBytes.decode())
                        break

                    print(f'dado recebido {msgReceivedBytes}')
                    file.write(msgReceivedBytes)
            escolha = str(input('Arquivo recebido com sucesso, gostaria de voltar ao menu? (s/n): '))

            if escolha == "s" or escolha == "S":
                pass
            elif escolha == "n" or escolha == "N":
                print("nao escolhido")
                break
