# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'clientEYbBCi.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(979, 720)
        MainWindow.setMinimumSize(QSize(640, 480))
        MainWindow.setMaximumSize(QSize(980, 720))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalWidget = QWidget(self.centralwidget)
        self.verticalWidget.setObjectName(u"verticalWidget")
        self.verticalWidget.setGeometry(QRect(630, 500, 281, 171))
        self.verticalWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.verticalWidget.setAutoFillBackground(False)
        self.verticalLayout = QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.prog = QProgressBar(self.verticalWidget)
        self.prog.setObjectName(u"prog")
        self.prog.setValue(0)

        self.verticalLayout.addWidget(self.prog)

        self.but_atualizar = QPushButton(self.verticalWidget)
        self.but_atualizar.setObjectName(u"but_atualizar")

        self.verticalLayout.addWidget(self.but_atualizar)

        self.but_baixar = QPushButton(self.verticalWidget)
        self.but_baixar.setObjectName(u"but_baixar")

        self.verticalLayout.addWidget(self.but_baixar)

        self.but_upload = QPushButton(self.verticalWidget)
        self.but_upload.setObjectName(u"but_upload")
        self.but_upload.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout.addWidget(self.but_upload)

        self.SrvFiles = QListWidget(self.centralwidget)
        self.SrvFiles.setObjectName(u"SrvFiles")
        self.SrvFiles.setGeometry(QRect(0, 50, 511, 641))
        self.lab_arquivos = QLabel(self.centralwidget)
        self.lab_arquivos.setObjectName(u"lab_arquivos")
        self.lab_arquivos.setGeometry(QRect(150, 20, 171, 31))
        self.lab_arquivos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.but_atualizar.setText(QCoreApplication.translate("MainWindow", u"Atualizar", None))
        self.but_baixar.setText(QCoreApplication.translate("MainWindow", u"Baixar", None))
        self.but_upload.setText(QCoreApplication.translate("MainWindow", u"Upload", None))
        self.lab_arquivos.setText(QCoreApplication.translate("MainWindow", u"Arquivos do Servidor", None))
    # retranslateUi

