import socket
import os
import threading

#Diretorio base onde fica os arquivos
basedir = 'Arquivos/'

#cria a conexão utilizando o protocolo UDP
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(('localhost', 55555))
print('Servidor escutando')

#váriaveis de controle do Go-Back-N
tamanhoJanela = 4
timeout = 5  # segundos
tamanho_pacote = 1024

base = 0 #primeiro numero da sequência
proxNum = 0 #próximo numero a ser enviado
eventAck = threading.Event()
addClient = None
pacotes = []

socket.timeout(timeout)

# Envia um pacote com numeração sequencial (4 bytes de header + dados)
def enviaPacote(numSeq):
    if numSeq < len(pacotes):
        seq_bytes = numSeq.to_bytes(4, byteorder='big')
        mensagem = seq_bytes + pacotes[numSeq]
        server.sendto(mensagem, addClient)
        print(f"Enviado pacote n{numSeq}")

def recebeAck():
    global base
    while base < len(pacotes):
        try:
            # server.settimeout(timeout)
            ackBytes, _ = server.recvfrom(1024)
            ackNum = int.from_bytes(ackBytes, byteorder='big')
            print(f"ACK n{ackNum} recebido")
            if ackNum >= base:
                base = ackNum + 1
                eventAck.set()
        except socket.timeout:
            print("Timeout! Reenviando janela...")
            eventAck.set()

def enviaArquivo(nome_arquivo):
    global pacotes, base, proxNum

    # Lê o arquivo e divide em pacotes
    try:
        with open(f'{basedir}/{nome_arquivo}', 'rb') as file:
            data = file.read()
            pacotes = [data[i:i + tamanho_pacote] for i in range(0, len(data), tamanho_pacote)]
    except FileNotFoundError:
        server.sendto(b'ERRO: arquivo nao encontrado', addClient)
        return

    print(f"Total de pacotes: {len(pacotes)}")

    base = 0
    proxNum = 0
    eventAck.clear()

    #inicia a thread para receber os ACKs
    ack_thread = threading.Thread(target=recebeAck)
    ack_thread.start()

    #loop de envio com janela deslizante
    while base < len(pacotes):
        while proxNum < base + tamanhoJanela and proxNum < len(pacotes):
            enviaPacote(proxNum)
            proxNum += 1

        eventAck.wait(timeout)
        eventAck.clear()

    ack_thread.join()

    # Envia EOF
    server.sendto(b'EOF', addClient)
    print("Arquivo enviado com sucesso.")

while True:
    msgClientBytes, addressClient = server.recvfrom(1024) #recebe a mensagem do cliente e armazena tanto a mensagem como também o endereço
    addClient = addressClient #armazena o endereço do cliente em outra variavel que irá ser utilizada no fluxo
    msgClientString = msgClientBytes.decode() #decotifica a mensagem para string

    print(f'arquivo escolhido pelo usuario: {msgClientString}')

    if msgClientString.startswith("UPLOAD "):
        nome_arquivo = msgClientString[7:]
        print(f"Recebendo upload de: {nome_arquivo}")

        pacotesRecebidos = {}
        while True:
            pacote, _ = server.recvfrom(2048)

            if pacote == b'EOF':
                print(f"Upload de {nome_arquivo} finalizado.")
                break

            numero_pacote = int.from_bytes(pacote[:4], 'big')
            dados = pacote[4:]
            pacotesRecebidos[numero_pacote] = dados
            print(f"Pacote #{numero_pacote} recebido ({len(dados)} bytes)")

            ack = numero_pacote.to_bytes(4, 'big')
            server.sendto(ack, addressClient)

        # salva os pacotes na pasta Arquivos/
        os.makedirs('Arquivos', exist_ok=True)
        with open(os.path.join('Arquivos', nome_arquivo), 'wb') as file:
            for i in range(len(pacotesRecebidos)):
                file.write(pacotesRecebidos[i])
        continue

    elif msgClientString == "LIST":
        Arquivos = []
        with os.scandir(basedir) as arquivos:
            for arquivo in arquivos:
                print(f'arquivo: {arquivo}')
                Arquivos.append(str(arquivo).split("'")[1])

        if not Arquivos:
            print("Sem arquivos na pasta")
            server.sendto("O servidor não possui nenhum arquivo, faça um upload para atualiza-lo!".encode(), addressClient)
        else:
            server.sendto(f'Lista de arquivos: {str(Arquivos)}'.encode(), addressClient)
            print(f"Enviado Lista de arquivos para: {addressClient}")
    else:
       print(f"Arquivo solicitado pelo cliente: {msgClientString}")
       enviaArquivo(msgClientString)

