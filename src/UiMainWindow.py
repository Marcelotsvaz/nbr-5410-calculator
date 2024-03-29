# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QWidget)

from genericModelViews.views import (GenericListView, GenericTreeView)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(1000, 600)
        self.actionNew = QAction(mainWindow)
        self.actionNew.setObjectName(u"actionNew")
        icon = QIcon()
        iconThemeName = u"document-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionNew.setIcon(icon)
        self.actionOpen = QAction(mainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon1 = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionOpen.setIcon(icon1)
        self.actionSave = QAction(mainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon2 = QIcon()
        iconThemeName = u"document-save"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionSave.setIcon(icon2)
        self.actionSaveAs = QAction(mainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        icon3 = QIcon()
        iconThemeName = u"document-save-as"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionSaveAs.setIcon(icon3)
        self.actionQuit = QAction(mainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        icon4 = QIcon()
        iconThemeName = u"application-exit"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionQuit.setIcon(icon4)
        self.actionAbout = QAction(mainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        icon5 = QIcon()
        iconThemeName = u"help-about"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.actionAbout.setIcon(icon5)
        self.centralWidget = QWidget(mainWindow)
        self.centralWidget.setObjectName(u"centralWidget")
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.projectTab = QWidget()
        self.projectTab.setObjectName(u"projectTab")
        self.gridLayout_4 = QGridLayout(self.projectTab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.suppliesListView = GenericListView(self.projectTab)
        self.suppliesListView.setObjectName(u"suppliesListView")

        self.gridLayout_4.addWidget(self.suppliesListView, 1, 0, 1, 1)

        self.loadTypesListView = GenericListView(self.projectTab)
        self.loadTypesListView.setObjectName(u"loadTypesListView")

        self.gridLayout_4.addWidget(self.loadTypesListView, 1, 1, 1, 1)

        self.wireTypesListView = GenericListView(self.projectTab)
        self.wireTypesListView.setObjectName(u"wireTypesListView")

        self.gridLayout_4.addWidget(self.wireTypesListView, 1, 2, 1, 1)

        self.suppliesLabel = QLabel(self.projectTab)
        self.suppliesLabel.setObjectName(u"suppliesLabel")

        self.gridLayout_4.addWidget(self.suppliesLabel, 0, 0, 1, 1)

        self.loadTypesLabel = QLabel(self.projectTab)
        self.loadTypesLabel.setObjectName(u"loadTypesLabel")

        self.gridLayout_4.addWidget(self.loadTypesLabel, 0, 1, 1, 1)

        self.wireTypesLabel = QLabel(self.projectTab)
        self.wireTypesLabel.setObjectName(u"wireTypesLabel")

        self.gridLayout_4.addWidget(self.wireTypesLabel, 0, 2, 1, 1)

        self.tabWidget.addTab(self.projectTab, "")
        self.circuitsTab = QWidget()
        self.circuitsTab.setObjectName(u"circuitsTab")
        self.gridLayout_2 = QGridLayout(self.circuitsTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.circuitsTreeView = GenericTreeView(self.circuitsTab)
        self.circuitsTreeView.setObjectName(u"circuitsTreeView")

        self.gridLayout_2.addWidget(self.circuitsTreeView, 1, 0, 1, 3)

        self.newCircuitButton = QPushButton(self.circuitsTab)
        self.newCircuitButton.setObjectName(u"newCircuitButton")
        icon6 = QIcon()
        iconThemeName = u"window-new"
        if QIcon.hasThemeIcon(iconThemeName):
            icon6 = QIcon.fromTheme(iconThemeName)
        else:
            icon6.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.newCircuitButton.setIcon(icon6)

        self.gridLayout_2.addWidget(self.newCircuitButton, 0, 2, 1, 1)

        self.deleteCircuitButton = QPushButton(self.circuitsTab)
        self.deleteCircuitButton.setObjectName(u"deleteCircuitButton")
        icon7 = QIcon()
        iconThemeName = u"delete"
        if QIcon.hasThemeIcon(iconThemeName):
            icon7 = QIcon.fromTheme(iconThemeName)
        else:
            icon7.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)

        self.deleteCircuitButton.setIcon(icon7)

        self.gridLayout_2.addWidget(self.deleteCircuitButton, 0, 1, 1, 1)

        self.tabWidget.addTab(self.circuitsTab, "")
        self.conduitsTab = QWidget()
        self.conduitsTab.setObjectName(u"conduitsTab")
        self.gridLayout_3 = QGridLayout(self.conduitsTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 0, 1, 1)

        self.newConduitRunButton = QPushButton(self.conduitsTab)
        self.newConduitRunButton.setObjectName(u"newConduitRunButton")
        self.newConduitRunButton.setIcon(icon6)

        self.gridLayout_3.addWidget(self.newConduitRunButton, 0, 2, 1, 1)

        self.deleteConduitRunButton = QPushButton(self.conduitsTab)
        self.deleteConduitRunButton.setObjectName(u"deleteConduitRunButton")
        self.deleteConduitRunButton.setIcon(icon7)

        self.gridLayout_3.addWidget(self.deleteConduitRunButton, 0, 1, 1, 1)

        self.conduitsTreeView = GenericTreeView(self.conduitsTab)
        self.conduitsTreeView.setObjectName(u"conduitsTreeView")

        self.gridLayout_3.addWidget(self.conduitsTreeView, 1, 0, 1, 3)

        self.tabWidget.addTab(self.conduitsTab, "")

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
        self.newCircuitButton.clicked.connect(self.circuitsTreeView.newItem)
        self.actionNew.triggered.connect(mainWindow.newProject)
        self.actionAbout.triggered.connect(mainWindow.showAbout)
        self.actionQuit.triggered.connect(mainWindow.close)
        self.deleteCircuitButton.clicked.connect(self.circuitsTreeView.deleteSelectedItems)
        self.newConduitRunButton.clicked.connect(self.conduitsTreeView.newItem)
        self.deleteConduitRunButton.clicked.connect(self.conduitsTreeView.deleteSelectedItems)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"NBR 5410 Calculator", None))
        self.actionNew.setText(QCoreApplication.translate("mainWindow", u"&New", None))
#if QT_CONFIG(shortcut)
        self.actionNew.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOpen.setText(QCoreApplication.translate("mainWindow", u"&Open...", None))
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave.setText(QCoreApplication.translate("mainWindow", u"&Save", None))
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveAs.setText(QCoreApplication.translate("mainWindow", u"Save &As...", None))
#if QT_CONFIG(shortcut)
        self.actionSaveAs.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionQuit.setText(QCoreApplication.translate("mainWindow", u"&Quit", None))
#if QT_CONFIG(shortcut)
        self.actionQuit.setShortcut(QCoreApplication.translate("mainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("mainWindow", u"&About", None))
        self.suppliesLabel.setText(QCoreApplication.translate("mainWindow", u"Supplies", None))
        self.loadTypesLabel.setText(QCoreApplication.translate("mainWindow", u"Load Types", None))
        self.wireTypesLabel.setText(QCoreApplication.translate("mainWindow", u"Wire Types", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.projectTab), QCoreApplication.translate("mainWindow", u"Project", None))
        self.newCircuitButton.setText(QCoreApplication.translate("mainWindow", u"New circuit", None))
        self.deleteCircuitButton.setText(QCoreApplication.translate("mainWindow", u"Delete circuit", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.circuitsTab), QCoreApplication.translate("mainWindow", u"Circuits", None))
        self.newConduitRunButton.setText(QCoreApplication.translate("mainWindow", u"New conduit run", None))
        self.deleteConduitRunButton.setText(QCoreApplication.translate("mainWindow", u"Delete conduit run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.conduitsTab), QCoreApplication.translate("mainWindow", u"Conduits", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainWindow", u"&Help", None))
    # retranslateUi

