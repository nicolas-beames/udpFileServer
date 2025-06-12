import sys
import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import QFile, Qt

sys.path.append("../Ui")
from ui_client import Ui_MainWindow

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip, porta = "localhost", 55555


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.but_upload.clicked.connect(self.upload_clicked)
        self.ui.but_listar.clicked.connect(self.listar_clicked)
        self.ui.but_baixar.clicked.connect(self.baixar_clicked)
        
    def listar_clicked(self):
        print("Listar Clicado")
        client.sendto("LIST".encode(), (ip, porta))
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
            if not self.ui.SrvFiles.findItems(item[:-1], Qt.MatchFixedString | Qt.MatchCaseSensitive):
                self.ui.SrvFiles.addItem(str(item[:-1]))

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
        msgClient = self.ui.SrvFiles.currentIndex().data()

        print(msgClient)
        client.sendto(msgClient.encode(), ('localhost', 55555))

        pacotesRecebidos = {}
        with open('copia_' + msgClient, 'wb') as file:
            while True:
                try:
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

                    dlg_sucesso = QMessageBox(self)
                    dlg_sucesso.setWindowTitle("Sucesso!")
                    dlg_sucesso.setText("Arquivo baixado com sucesso!\n Ele estara na pasta do script/exe")
                    btn_ok = dlg_sucesso.exec()

                    if btn_ok == QMessageBox.Ok:
                        print("Operação concluida com exito! Finalizando...")
                except:
                    print("Erro!")
                finally:
                    break

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
