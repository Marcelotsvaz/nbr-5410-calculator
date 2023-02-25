# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QMainWindow,
    QPushButton, QSizePolicy, QStatusBar, QTableView,
    QWidget)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(800, 600)
        self.centralWidget = QWidget(mainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.saveButtion = QPushButton(self.centralWidget)
        self.saveButtion.setObjectName(u"saveButtion")

        self.gridLayout.addWidget(self.saveButtion, 2, 3, 1, 1)

        self.loadButton = QPushButton(self.centralWidget)
        self.loadButton.setObjectName(u"loadButton")

        self.gridLayout.addWidget(self.loadButton, 2, 2, 1, 1)

        self.tableView = QTableView(self.centralWidget)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setAlternatingRowColors(True)

        self.gridLayout.addWidget(self.tableView, 1, 2, 1, 2)

        mainWindow.setCentralWidget(self.centralWidget)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        self.saveButtion.clicked.connect(mainWindow.saveProject)
        self.loadButton.clicked.connect(mainWindow.loadProject)

        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"NBR 5410 Calculator", None))
        self.saveButtion.setText(QCoreApplication.translate("mainWindow", u"Save", None))
        self.loadButton.setText(QCoreApplication.translate("mainWindow", u"Load", None))
    # retranslateUi

