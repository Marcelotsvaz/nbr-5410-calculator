# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.7.1
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

from nbr_5410_calculator.circuitsTab import CircuitsView
from nbr_5410_calculator.conduitsTab import (ConduitRunsView, UnassignedCircuitsView)
from nbr_5410_calculator.projectTab import (LoadTypeView, SupplyView, WireTypeView)

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
        self.projectTab = QWidget()
        self.projectTab.setObjectName(u"projectTab")
        self.gridLayout_4 = QGridLayout(self.projectTab)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.newSupplyButton = QPushButton(self.projectTab)
        self.newSupplyButton.setObjectName(u"newSupplyButton")
        icon6 = QIcon(QIcon.fromTheme(u"contact-new"))
        self.newSupplyButton.setIcon(icon6)

        self.gridLayout_4.addWidget(self.newSupplyButton, 0, 2, 1, 1)

        self.newWireTypeButton = QPushButton(self.projectTab)
        self.newWireTypeButton.setObjectName(u"newWireTypeButton")
        self.newWireTypeButton.setIcon(icon6)

        self.gridLayout_4.addWidget(self.newWireTypeButton, 0, 8, 1, 1)

        self.loadTypesLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.loadTypesLabelSpacer, 0, 4, 1, 1)

        self.loadTypesLabel = QLabel(self.projectTab)
        self.loadTypesLabel.setObjectName(u"loadTypesLabel")

        self.gridLayout_4.addWidget(self.loadTypesLabel, 0, 3, 1, 1)

        self.wireTypesLabel = QLabel(self.projectTab)
        self.wireTypesLabel.setObjectName(u"wireTypesLabel")

        self.gridLayout_4.addWidget(self.wireTypesLabel, 0, 6, 1, 1)

        self.loadTypesView = LoadTypeView(self.projectTab)
        self.loadTypesView.setObjectName(u"loadTypesView")

        self.gridLayout_4.addWidget(self.loadTypesView, 1, 3, 1, 3)

        self.suppliesLabel = QLabel(self.projectTab)
        self.suppliesLabel.setObjectName(u"suppliesLabel")

        self.gridLayout_4.addWidget(self.suppliesLabel, 0, 0, 1, 1)

        self.suppliesView = SupplyView(self.projectTab)
        self.suppliesView.setObjectName(u"suppliesView")

        self.gridLayout_4.addWidget(self.suppliesView, 1, 0, 1, 3)

        self.suppliesLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.suppliesLabelSpacer, 0, 1, 1, 1)

        self.newLoadTypeButton = QPushButton(self.projectTab)
        self.newLoadTypeButton.setObjectName(u"newLoadTypeButton")
        self.newLoadTypeButton.setIcon(icon6)

        self.gridLayout_4.addWidget(self.newLoadTypeButton, 0, 5, 1, 1)

        self.wireTypesView = WireTypeView(self.projectTab)
        self.wireTypesView.setObjectName(u"wireTypesView")

        self.gridLayout_4.addWidget(self.wireTypesView, 1, 6, 1, 3)

        self.wireTypesLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.wireTypesLabelSpacer, 0, 7, 1, 1)

        self.tabWidget.addTab(self.projectTab, "")
        self.circuitsTab = QWidget()
        self.circuitsTab.setObjectName(u"circuitsTab")
        self.gridLayout_2 = QGridLayout(self.circuitsTab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.deleteCircuitButton = QPushButton(self.circuitsTab)
        self.deleteCircuitButton.setObjectName(u"deleteCircuitButton")
        icon7 = QIcon(QIcon.fromTheme(u"delete"))
        self.deleteCircuitButton.setIcon(icon7)

        self.gridLayout_2.addWidget(self.deleteCircuitButton, 0, 2, 1, 1)

        self.circuitsLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.circuitsLabelSpacer, 0, 1, 1, 1)

        self.newCircuitButton = QPushButton(self.circuitsTab)
        self.newCircuitButton.setObjectName(u"newCircuitButton")
        icon8 = QIcon(QIcon.fromTheme(u"window-new"))
        self.newCircuitButton.setIcon(icon8)

        self.gridLayout_2.addWidget(self.newCircuitButton, 0, 4, 1, 1)

        self.newUpstreamCircuitButton = QPushButton(self.circuitsTab)
        self.newUpstreamCircuitButton.setObjectName(u"newUpstreamCircuitButton")
        self.newUpstreamCircuitButton.setIcon(icon8)

        self.gridLayout_2.addWidget(self.newUpstreamCircuitButton, 0, 3, 1, 1)

        self.circuitsLabel = QLabel(self.circuitsTab)
        self.circuitsLabel.setObjectName(u"circuitsLabel")

        self.gridLayout_2.addWidget(self.circuitsLabel, 0, 0, 1, 1)

        self.circuitsView = CircuitsView(self.circuitsTab)
        self.circuitsView.setObjectName(u"circuitsView")

        self.gridLayout_2.addWidget(self.circuitsView, 1, 0, 1, 5)

        self.tabWidget.addTab(self.circuitsTab, "")
        self.conduitsTab = QWidget()
        self.conduitsTab.setObjectName(u"conduitsTab")
        self.gridLayout_3 = QGridLayout(self.conduitsTab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.conduitRunsLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.conduitRunsLabelSpacer, 0, 1, 1, 1)

        self.newConduitRunButton = QPushButton(self.conduitsTab)
        self.newConduitRunButton.setObjectName(u"newConduitRunButton")
        self.newConduitRunButton.setIcon(icon8)

        self.gridLayout_3.addWidget(self.newConduitRunButton, 0, 3, 1, 1)

        self.deleteConduitRunButton = QPushButton(self.conduitsTab)
        self.deleteConduitRunButton.setObjectName(u"deleteConduitRunButton")
        self.deleteConduitRunButton.setIcon(icon7)

        self.gridLayout_3.addWidget(self.deleteConduitRunButton, 0, 2, 1, 1)

        self.conduitRunsLabel = QLabel(self.conduitsTab)
        self.conduitRunsLabel.setObjectName(u"conduitRunsLabel")

        self.gridLayout_3.addWidget(self.conduitRunsLabel, 0, 0, 1, 1)

        self.conduitsView = ConduitRunsView(self.conduitsTab)
        self.conduitsView.setObjectName(u"conduitsView")

        self.gridLayout_3.addWidget(self.conduitsView, 1, 0, 1, 4)

        self.unassignedCircuitsView = UnassignedCircuitsView(self.conduitsTab)
        self.unassignedCircuitsView.setObjectName(u"unassignedCircuitsView")

        self.gridLayout_3.addWidget(self.unassignedCircuitsView, 3, 0, 1, 4)

        self.unassigedCircuitsLabel = QLabel(self.conduitsTab)
        self.unassigedCircuitsLabel.setObjectName(u"unassigedCircuitsLabel")

        self.gridLayout_3.addWidget(self.unassigedCircuitsLabel, 2, 0, 1, 1)

        self.unassigedCircuitsLabelSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.unassigedCircuitsLabelSpacer, 2, 1, 1, 3)

        self.tabWidget.addTab(self.conduitsTab, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 4)

        mainWindow.setCentralWidget(self.centralWidget)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(mainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1000, 22))
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
        self.newCircuitButton.clicked.connect(self.circuitsView.newCircuit)
        self.actionNew.triggered.connect(mainWindow.newProject)
        self.actionAbout.triggered.connect(mainWindow.showAbout)
        self.actionQuit.triggered.connect(mainWindow.close)
        self.deleteCircuitButton.clicked.connect(self.circuitsView.deleteSelectedItems)
        self.newConduitRunButton.clicked.connect(self.conduitsView.newConduitRun)
        self.deleteConduitRunButton.clicked.connect(self.conduitsView.deleteSelectedItems)
        self.newUpstreamCircuitButton.clicked.connect(self.circuitsView.newUpstreamCircuit)
        self.newSupplyButton.clicked.connect(self.suppliesView.newSupply)
        self.newLoadTypeButton.clicked.connect(self.loadTypesView.newLoadType)
        self.newWireTypeButton.clicked.connect(self.wireTypesView.newWireType)

        self.tabWidget.setCurrentIndex(0)


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
        self.loadTypesLabel.setText(QCoreApplication.translate("mainWindow", u"Load Types", None))
        self.wireTypesLabel.setText(QCoreApplication.translate("mainWindow", u"Wire Types", None))
        self.suppliesLabel.setText(QCoreApplication.translate("mainWindow", u"Supplies", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.projectTab), QCoreApplication.translate("mainWindow", u"Project", None))
        self.deleteCircuitButton.setText(QCoreApplication.translate("mainWindow", u"Delete circuit", None))
        self.newCircuitButton.setText(QCoreApplication.translate("mainWindow", u"New circuit", None))
        self.newUpstreamCircuitButton.setText(QCoreApplication.translate("mainWindow", u"New upstream circuit", None))
        self.circuitsLabel.setText(QCoreApplication.translate("mainWindow", u"Circuits", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.circuitsTab), QCoreApplication.translate("mainWindow", u"Circuits", None))
        self.newConduitRunButton.setText(QCoreApplication.translate("mainWindow", u"New conduit run", None))
        self.deleteConduitRunButton.setText(QCoreApplication.translate("mainWindow", u"Delete conduit run", None))
        self.conduitRunsLabel.setText(QCoreApplication.translate("mainWindow", u"Conduit Runs", None))
        self.unassigedCircuitsLabel.setText(QCoreApplication.translate("mainWindow", u"Unassigned Circuits", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.conduitsTab), QCoreApplication.translate("mainWindow", u"Conduits", None))
        self.menuFile.setTitle(QCoreApplication.translate("mainWindow", u"&File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("mainWindow", u"&Help", None))
    # retranslateUi

