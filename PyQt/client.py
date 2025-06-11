import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QFile

sys.path.append("../Ui")
from ui_client import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.but_upload.clicked.connect(self.upload_clicked)

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
                self.file_list.addItems([str(Path(filename)) for filename in filenames])


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
