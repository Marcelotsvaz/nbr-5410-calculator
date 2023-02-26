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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QWidget)

from circuitsTab import CircuitsTableView

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(1000, 600)
        self.actionNew = QAction(mainWindow)
        self.actionNew.setObjectName(u"actionNew")
        icon = QIcon(QIcon.fromTheme(u"document-new"))
        self.actionNew.setIcon(icon)
        self.actionOpen = QAction(mainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon1 = QIcon(QIcon.fromTheme(u"document-open"))
        self.actionOpen.setIcon(icon1)
        self.actionSave = QAction(mainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon2 = QIcon(QIcon.fromTheme(u"document-save"))
        self.actionSave.setIcon(icon2)
        self.actionSaveAs = QAction(mainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        icon3 = QIcon(QIcon.fromTheme(u"document-save-as"))
        self.actionSaveAs.setIcon(icon3)
        self.actionQuit = QAction(mainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon4 = QIcon(QIcon.fromTheme(u"application-exit"))
        self.actionQuit.setIcon(icon4)
        self.actionAbout = QAction(mainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon5 = QIcon(QIcon.fromTheme(u"help-about"))
        self.actionAbout.setIcon(icon5)
        self.centralWidget = QWidget(mainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.panelTab = QWidget()
        self.panelTab.setObjectName(u"panelTab")
        self.tabWidget.addTab(self.panelTab, "")
        self.circuitsTab = QWidget()
        self.circuitsTab.setObjectName(u"circuitsTab")
        self.gridLayout_2 = QGridLayout(self.circuitsTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.newCircuitButton = QPushButton(self.circuitsTab)
        self.newCircuitButton.setObjectName(u"newCircuitButton")
        icon6 = QIcon(QIcon.fromTheme(u"window-new"))
        self.newCircuitButton.setIcon(icon6)

        self.gridLayout_2.addWidget(self.newCircuitButton, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.circuitsTableView = CircuitsTableView(self.circuitsTab)
        self.circuitsTableView.setObjectName(u"circuitsTableView")
        self.circuitsTableView.setAlternatingRowColors(True)
        self.circuitsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.circuitsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.circuitsTableView.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.circuitsTableView.horizontalHeader().setProperty("showSortIndicator", True)
        self.circuitsTableView.horizontalHeader().setStretchLastSection(True)

        self.gridLayout_2.addWidget(self.circuitsTableView, 1, 0, 1, 2)

        self.tabWidget.addTab(self.circuitsTab, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.tabWidget.addTab(self.tab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 4)

        mainWindow.setCentralWidget(self.centralWidget)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(mainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1000, 30))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        mainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(mainWindow)
        self.actionSave.triggered.connect(mainWindow.saveProject)
        self.actionOpen.triggered.connect(mainWindow.loadProject)
        self.actionSaveAs.triggered.connect(mainWindow.saveProject)
        self.newCircuitButton.clicked.connect(self.circuitsTableView.newCircuit)
        self.actionNew.triggered.connect(mainWindow.newProject)
        self.actionAbout.triggered.connect(mainWindow.showAbout)
        self.actionQuit.triggered.connect(mainWindow.close)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"NBR 5410 Calculator", None))
        self.actionNew.setText(QCoreApplication.translate("mainWindow", u"New", None))
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("mainWindow", u"Open...", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("mainWindow", u"Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveAs.setText(QCoreApplication.translate("mainWindow", u"Save As...", None))
#if QT_CONFIG(shortcut)
        self.actionSaveAs.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("mainWindow", u"Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("mainWindow", u"About", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.panelTab), QCoreApplication.translate("mainWindow", u"Panel", None))
        self.newCircuitButton.setText(QCoreApplication.translate("mainWindow", u"New circuit", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.circuitsTab), QCoreApplication.translate("mainWindow", u"Circuits", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("mainWindow", u"Conduits", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainWindow", u"Help", None))
    # retranslateUi

