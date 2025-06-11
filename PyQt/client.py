import sys
import socket
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
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
            if item.endswith('"<DirEntry \\'):
                lista.remove(item)
        for item in lista:
            if not item.endswith("\\"):
                lista.remove(item)
        lista.pop()

        # Verifica se o item ja está na lista
        # caso não estiver ele insere
        for item in lista:
            if not self.ui.SrvFiles.findItems(item[:-1], Qt.MatchFixedString | Qt.MatchCaseSensitive):
                self.ui.SrvFiles.addItem(str(item[:-1]))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
