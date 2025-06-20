import socket # biblioteca responsável por realizar as conexões entre servidor e cliente
import random # biblioteca utilizada parar gerar números aleatórios, essa biblioteca é utilizada nas funções que simulam a perda de pacotes e acks
import os # biblioteca utilizada para retornar funções do sistema
import tkinter as tk # biblioteca utilizada para gerar interfaces 
from tkinter import filedialog # biblioteca responsável por criar a tela de upload de arquivos

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip_servidor = input("Digite o IP do servidor: ").strip()
porta_servidor = 55555

# #
# Função responsável por simular a perda de pacotes ao receber.
# parametro (client) recebe a credencial do usuario
# parametro (buffer_size) recebe a quantidade de bytes que a mensagen irá receber
# parametro (loss_rate) tem como valor "0.1", que simula a probabilidade de perda de 10%
# #
def recebeComPerda(client, buffer_size, loss_rate=0.1, timeout=5):
    client.settimeout(timeout) # Define o timeout para a chamada recvfrom
    try:
        msg, addr = client.recvfrom(buffer_size)
        if random.random() < loss_rate:
            print("** Pacote PERDIDO (simulado) **")
            return None, None # Simula a perda retornando None
        return msg, addr
    except socket.timeout:
        # print("Timeout na recepção (simulado).") # O loop principal tratará disso
        return None, None
    except Exception as e:
        print(f"Erro ao receber dados: {e}")
        return None, None

# #
# Função responsável por simular a parda de ACK ao enviar.
# parametro (client) recebe a credencial do usuario
# parametro (ack_bytes) recebe a quantidade de bytes que o ack irá receber
# parametro (addr) recebe a credencial do servidor
# parametro (loss_rate) tem como valor "0.1", que simula a probabilidade de perda de 10%
# #
def enviaAckComPerda(client, ack_bytes, addr, loss_rate=0.1):
    if random.random() < loss_rate:
        print(f"** ACK PERDIDO (simulado) para #{int.from_bytes(ack_bytes, 'big')} **")
        return  # não envia o ACK
    client.sendto(ack_bytes, addr)
    print(f"ACK #{int.from_bytes(ack_bytes, 'big')} enviado")
    

# #
# Função responsável por criar arquivos.
# parametro (origem): recebe a origem do arquivo selecionado para abrir o arquivo no modo de leitura binaria
# parametro (destino): recebe o destino de onde o arquivo selecionaro ira ser criado, utilizando a escrita binaria
# #
def criaArquivo(origem, destino):
    with open(origem, 'rb') as origemArquivo, open(destino,'wb') as destinoArquivo:
        while True:
            chunk = origemArquivo.read(1024 * 1024)
            if not chunk:
                break
            destinoArquivo.write(chunk)

# #
# Função responsável por realizar o upload dos arquivos para o servidor
# quando essa função é chamada, uma tela utilizando a biblioteca (TKinder) é exibida, essa tela permite que arquivos sejam selecionados, esses arquivos serão utilizados para envio ao servidor. 
# #
def fazerUpload():
    root = tk.Tk()
    root.withdraw()

    caminhoArquivo = filedialog.askopenfilename(title="Selecione o arquivo que deseja inserir")

    root.update()  # a seleção de arquivo ocorre antes de fechar a tela
    root.destroy()  # fecha a tela após seleção do arquivo

    if caminhoArquivo:
        nomeArquivo = os.path.basename(caminhoArquivo)
        pastaDestino = "Uploads"
        os.makedirs(pastaDestino, exist_ok=True)
    
        destino = os.path.join(pastaDestino, nomeArquivo)
        criaArquivo(caminhoArquivo, destino)

# #
# Loop principal, responsável por manter o menu aberto
# #
while True:

    print("\n=== MENU ===")
    print("0 - Sair")
    print("1 - Listar arquivos")
    print("2 - Baixar do Servidor")
    print("3 - Fazer upload")
    print("4 - Atualizar Servidor")

    dontCloseDownloads = True # variavel de controle do loop de downloads

    try:
        opt = int(input('Digite uma opção: '))
    except ValueError:
        print("Digite um número válido.")
        continue

    if opt == 0:
        print("Volte sempre!")
        break

    match opt:
        # #
        # Caso o usuario selecione a opção 1 a seguinte lógica é executada:
        # 1 - o código envia uma mensagem contendo "LIST" para o servidor.
        # 2 - o servidor recebe essa informação e entende que deve retornar a lista de arquivos.
        # 3 - com base no retorno do servidor, o código realiza validações para ver se o servidor já terminou sua mensagem, e exibe o retorno para o usuario.
        # #
        case 1:
            client.sendto("LIST".encode(), (ip_servidor, porta_servidor))
            msgReceivedBytes, addressServer = client.recvfrom(1024)

            if msgReceivedBytes == b'EOF':
                break

            if msgReceivedBytes.startswith(b'ERRO'):
                print(msgReceivedBytes.decode())
                break

            print(msgReceivedBytes.decode())
            pass

        # #
        # Caso o usuario selecione a opção 2 a seguinte lógica é executada:
        # 1 - o while é iniciado, utilizando a variavel "dontCloseDownloads" como controle para finalização do loop.
        # 2 - envia o nome do arquivo para o servidor.
        # 3 - baseado no retorno do servidor, o código realiza o protocolo Go Back N para o recebimento dos pacotes do arquivo escolhido, os pacotes são gravados e o arquivo é criado na pasta "Downloads".
        # 4 - após o recebimento completo do arquivo, o cliente é perguntado se deseja baixar mais algum arquivo, com base no retorno do usuario, a variavel "dontCloseDownloads" segue com o valor igual a True, caso o contrario aconteça a variavel recebe o valor "False", com isso o loop é encerrado.
        # #
        case 2:
            while dontCloseDownloads:
                msgClient = str(input("Qual arquivo gostaria de baixar? (arquivo.extensao): "))
                client.sendto(msgClient.encode(), (ip_servidor, porta_servidor))

                client.settimeout(5) # Ajuste este timeout se necessário

                pacotesRecebidos = {}
                esperado = 0 # O próximo número de sequência esperado
                arquivo_completo = False
                os.makedirs('Downloads', exist_ok=True)
                
                with open(os.path.join('Downloads', msgClient), 'wb') as file:
                    while not arquivo_completo:
                        try:
                            resultado = recebeComPerda(client, 2048, loss_rate=0.1, timeout=5) 

                            if resultado == (None, None): 

                                print("Esperando por pacote. Timeout ou perda simulada. Reenviando último ACK.")

                                if esperado > 0: 
                                    ack_anterior = (esperado - 1).to_bytes(4, byteorder='big')
                                    client.sendto(ack_anterior, (ip_servidor, porta_servidor))
                                    print(f"ACK {esperado - 1} reenviado devido a timeout/perda.")
                                continue 

                            msgReceivedBytes, addressServer = resultado

                            if msgReceivedBytes.startswith(b'ERRO'):
                                print(msgReceivedBytes.decode())
                                break 

                            if msgReceivedBytes == b'EOF':
                                print("Mensagem EOF recebida. Finalizando download.")
                                arquivo_completo = True 
                                client.sendto(b'ACK_EOF', addressServer) 
                                continue
                            
                            numero_pacote = int.from_bytes(msgReceivedBytes[:4], byteorder='big')
                            dados_pacote = msgReceivedBytes[4:]

                            if numero_pacote == esperado:
                                print(f'Pacote #{numero_pacote} recebido com {len(dados_pacote)} bytes')
                                pacotesRecebidos[numero_pacote] = dados_pacote 
                                enviaAckComPerda(client, numero_pacote.to_bytes(4, byteorder='big'), addressServer)
                                esperado += 1 
                            else:
                                if esperado > 0:
                                    enviaAckComPerda(client, (esperado - 1).to_bytes(4, byteorder='big'), addressServer)
                                else:
                                    print(f"Pacote {numero_pacote} recebido mas esperado {esperado}. Ignorando.")

                        except socket.timeout:
                            print("Timeout no cliente. Solicitando reenvio de pacotes...")
                            if esperado > 0:
                                ack_para_reenviar = (esperado - 1).to_bytes(4, byteorder='big')
                                client.sendto(ack_para_reenviar, (ip_servidor, porta_servidor))
                                print(f"ACK {esperado - 1} reenviado para solicitar retransmissão.")
                            else: 
                                print("Primeiro pacote não chegou ou houve timeout inicial. Reenviando requisição do arquivo.")
                                client.sendto(msgClient.encode(), (ip_servidor, porta_servidor))


                    if arquivo_completo:
                        print(f"Escrevendo {esperado} pacotes no arquivo.")
                        for i in range(esperado):
                            if i in pacotesRecebidos:
                                file.write(pacotesRecebidos[i])
                            else:
                                print(f"AVISO: Pacote {i} ausente. O arquivo pode estar corrompido.")
                                break

                if arquivo_completo:
                    os.path.join('Downloads', msgClient)
                    print(f"Arquivo '{msgClient}' salvo com sucesso em 'Downloads/'.")
              
                else:
                    print(f"Download de '{msgClient}' não foi concluído.")
                    if os.path.exists(os.path.join('Downloads', msgClient)):
                        os.remove(os.path.join('Downloads', msgClient))


                client.settimeout(None) 

                escolha = str(input('Gostaria de baixar mais algum arquivo? (s/n): '))
                if escolha.lower() == "s":
                    dontCloseDownloads = True
                else:
                    dontCloseDownloads = False

        # #
        # Caso o usuario selecione a opção 3 a seguinte lógica é executada:
        # 1 - chama a função "fazerUpload", para saber mais sobre a função, verifique a documentação dela.
        # #
        case 3:
            fazerUpload()
            pass

        # #
        # Caso o usuario selecione a opção 4 a seguinte lógica é executada:
        # 1 - verifica se existem arquivos na pasta "Uplodas"
        # 2 - caso não tenha nenhum arquivo, o código finaliza o fluxo da opção 4
        # 3 - se existir arquivos, um loop é execurado e os arquivos são enviados para o servidor
        # 4 - o envio dos arquivos para o servidor utilica o protocolo Go Back N
        # #
        case 4:
            print('Enviando arquivos da pasta Uploads para o servidor com Go-Back-N...')

            arquivos = os.listdir("Uploads")
            if not arquivos:
                print("Nenhum arquivo para enviar.")
                break

            for nome_arquivo in arquivos:
                caminho_arquivo = os.path.join("Uploads", nome_arquivo)
                try:
                    with open(caminho_arquivo, 'rb') as file:
                        dados = file.read()
                        pacotes = [dados[i:i + 1024] for i in range(0, len(dados), 1024)]
                except FileNotFoundError:
                    print(f"Arquivo {nome_arquivo} não encontrado.")
                    continue

                base = 0
                proxNum = 0
                tamanhoJanela = 4
                timeout = 2

                # Envia comando de upload com o nome do arquivo
                comando = f"UPLOAD {nome_arquivo}"
                client.sendto(comando.encode(), (ip_servidor, porta_servidor))

                client.settimeout(timeout)
                print(f"Iniciando envio de {nome_arquivo} ({len(pacotes)} pacotes)...")

                while base < len(pacotes):
                    while proxNum < base + tamanhoJanela and proxNum < len(pacotes):
                        seq_bytes = proxNum.to_bytes(4, 'big')
                        pacote = seq_bytes + pacotes[proxNum]
                        client.sendto(pacote, (ip_servidor, porta_servidor))
                        print(f"Enviado pacote {proxNum}")
                        proxNum += 1

                    try:
                        ackBytes, _ = client.recvfrom(1024)
                        ackNum = int.from_bytes(ackBytes, byteorder='big')
                        print(f"ACK {ackNum} recebido")

                        if ackNum >= base:
                            base = ackNum + 1
                    except socket.timeout:
                        print("Timeout. Reenviando janela...")
                        proxNum = base  # reinicia do último ACK válido

                # Envia EOF
                client.sendto(b'EOF', (ip_servidor, porta_servidor))
                print(f"{nome_arquivo} enviado com sucesso.\n")

        # #
        # Caso o usuario selecione uma opção diferente das demais, um print é executado avisando que a opção selecionada é inválida.
        # #
        case _:
            print("Opção inválida. Tente novamente.")

