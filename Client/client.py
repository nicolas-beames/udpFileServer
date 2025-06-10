import socket


while True:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    msgClient = str(input('digite o nome do arquivo que deseja receber: '))

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

    print('arquivo recebido')