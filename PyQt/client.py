import sys
import os
import random
import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QFile, Qt

sys.path.append("../Ui")
from ui_client import Ui_MainWindow

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip_servidor, porta_servidor = "192.168.1.33", 55555


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.but_upload.clicked.connect(self.upload_clicked)
        self.ui.but_atualizar.clicked.connect(self.atualizar_clicked)
        self.ui.but_baixar.clicked.connect(self.baixar_clicked)
        self.atualizar_clicked()
        
    def atualizar_clicked(self):
        print("Atualizar Clicado")
        client.sendto("LIST".encode(), (ip_servidor, porta_servidor))
        msgReceivedBytes, addressServer = client.recvfrom(1024)

        if msgReceivedBytes.startswith(b'ERRO'):
            print("Erro!")

        # Tratativa para a lista dos arquivos recebida do Srv
        lista = str(msgReceivedBytes).split("\'")
        lista = list(lista)
        for item in lista:
            if item.endswith('Entry \\') or not item.endswith("\\"):
                lista.remove(item)
        lista.pop()
        lista.pop(0)

        # Verifica se o item ja está na lista
        # caso não estiver ele insere
        for item in lista:
            if not self.ui.SrvFiles.findItems(item, Qt.MatchFixedString | Qt.MatchCaseSensitive):
                self.ui.SrvFiles.addItem(str(item))

    def upload_clicked(self):
        print("DEBUG: Upload Clicado")
        upload_selecionar = QFileDialog(self)
        upload_selecionar = QFileDialog(self)
        upload_selecionar.setDirectory(r'C:\images')
        upload_selecionar.setFileMode(QFileDialog.FileMode.ExistingFiles)
        upload_selecionar.setViewMode(QFileDialog.ViewMode.List)
        if upload_selecionar.exec():
            filenames = upload_selecionar.selectedFiles()
            if filenames:
                #self.file_list.addItems([str(Path(filename)) for filename in filenames])
                pass

    def baixar_clicked(self):
        msgClient = str(self.ui.SrvFiles.currentIndex().data())
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
            dlg_sucesso = QMessageBox(self)
            dlg_sucesso.setWindowTitle("Sucesso!")
            dlg_sucesso.setText("Arquivo baixado com sucesso!\n Ele estara na pasta do script/exe")
            btn_ok = dlg_sucesso.exec()

            if btn_ok == QMessageBox.Ok:
                print("Operação concluida com exito! Finalizando...")
        else:
            print(f"Download de '{msgClient}' não foi concluído.")
            if os.path.exists(os.path.join('Downloads', msgClient)):
                os.remove(os.path.join('Downloads', msgClient))
            dlg_erro = QMessageBox(self)
            dlg_erro.setWindowTitle("Erro!")
            dlg_erro.setText("Ocorreu um erro! Arquivo não baixado...")
            btn_ok = dlg_erro.exec()

            if btn_ok == QMessageBox.Ok:
                print("Operação concluida com erro! Finalizando...")

        client.settimeout(None) 
    

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

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
