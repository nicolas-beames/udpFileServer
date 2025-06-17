import socket # biblioteca responsável por realizar as conexões entre servidor e cliente
import os # biblioteca utilizada para retornar funções do sistema
import threading # biblioteca responsável por permitir que o funcionamento ocorra em threads

#Diretorio base onde fica os arquivos
basedir = 'Arquivos/'

hostName = socket.gethostname()
ipAdd = socket.gethostbyname(hostName)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((ipAdd, 55555))
print(f'Servidor escutando no ip: {ipAdd} : 55555')

#váriaveis de controle do Go-Back-N
tamanhoJanela = 4 # quantidade de pacotes enviados por janela
timeout = 5  # segundos
tamanho_pacote = 1024 # tamanho do pacote em bytes

base = 0 #primeiro numero da sequência
proxNum = 0 #próximo numero a ser enviado
eventAck = threading.Event()
addClient = None
pacotes = []

# #
# Função responsável por pacotes com numeracao sequencial.
# parametro (numSeq) recebe o numero do pacote que será enviado
# #
def enviaPacote(numSeq):
    if numSeq < len(pacotes):
        seq_bytes = numSeq.to_bytes(4, byteorder='big')
        mensagem = seq_bytes + pacotes[numSeq]
        server.sendto(mensagem, addClient)
        print(f"Enviado pacote n{numSeq}")

# #
# Função responsável por receber os ACKs.
# dependendo do recebimento do ACK, a janela é reenvidada
# #
def recebeAck():
    global base, proxNum
    while base < len(pacotes):
        try:
            server.settimeout(timeout)
            ackBytes, _ = server.recvfrom(1024)
            ackNum = int.from_bytes(ackBytes, byteorder='big')
            print(f"ACK n{ackNum} recebido")
            if ackNum >= base:
                base = ackNum + 1
                eventAck.set()
        except socket.timeout:
            print("Timeout! Reenviando janela...")
            proxNum = base  # Reinicia para reenviar janela
            eventAck.set()

# #
# Função responsável por enviar os arquivos
# parametro (nome_arquivo) recebe o nome do arquivo que irá ser enviado
# a lógica utilizada para o envio é o protocolo Go Back N
# #
def enviaArquivo(nome_arquivo):
    global pacotes, base, proxNum # variaveis de controle

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

    # --- NOVO: Lógica para enviar EOF e esperar ACK ---
    server.settimeout(timeout) # Define um timeout para o servidor esperar o ACK do EOF
    eof_enviado = False
    tentativas_eof = 0
    max_tentativas_eof = 5 # Tenta enviar o EOF algumas vezes

    while not eof_enviado and tentativas_eof < max_tentativas_eof:
        try:
            server.sendto(b'EOF', addClient)
            print("EOF enviado. Esperando ACK_EOF...")
            ack_eof, _ = server.recvfrom(1024)
            if ack_eof == b'ACK_EOF':
                print("ACK_EOF recebido. Arquivo enviado com sucesso.")
                eof_enviado = True
            else:
                print(f"ACK_EOF esperado, mas recebeu: {ack_eof}. Reenviando EOF.")
        except socket.timeout:
            print("Timeout esperando ACK_EOF. Reenviando EOF.")
        except Exception as e:
            print(f"Erro ao enviar/receber ACK_EOF: {e}. Reenviando EOF.")
        tentativas_eof += 1

    if not eof_enviado:
        print("Falha ao enviar EOF após múltiplas tentativas.")
    
    server.settimeout(None) # Volta para timeout padrão (bloqueante)


# #
# Loop principal, responsável por manter a o fluxo e o servidor em andamento, para recebimento e envio de arquivos 
# #
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

