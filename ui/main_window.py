# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(624, 524)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.game_pat_label = QLabel(self.centralwidget)
        self.game_pat_label.setObjectName("game_pat_label")

        self.horizontalLayout.addWidget(self.game_pat_label)

        self.game_path_input = QLineEdit(self.centralwidget)
        self.game_path_input.setObjectName("game_path_input")

        self.horizontalLayout.addWidget(self.game_path_input)

        self.game_path_browse = QPushButton(self.centralwidget)
        self.game_path_browse.setObjectName("game_path_browse")

        self.horizontalLayout.addWidget(self.game_path_browse)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.patch_button = QPushButton(self.centralwidget)
        self.patch_button.setObjectName("patch_button")

        self.horizontalLayout_2.addWidget(self.patch_button)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.log_tab = QWidget()
        self.log_tab.setObjectName("log_tab")
        self.verticalLayout = QVBoxLayout(self.log_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.log = QTextEdit(self.log_tab)
        self.log.setObjectName("log")

        self.verticalLayout.addWidget(self.log)

        self.tabWidget.addTab(self.log_tab, "")
        self.skin_tab = QWidget()
        self.skin_tab.setObjectName("skin_tab")
        self.horizontalLayout_3 = QHBoxLayout(self.skin_tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget.addTab(self.skin_tab, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 624, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Tomba! Patcher", None)
        )
        self.game_pat_label.setText(
            QCoreApplication.translate("MainWindow", "ISO/BIN:", None)
        )
        self.game_path_browse.setText(
            QCoreApplication.translate("MainWindow", "Browse...", None)
        )
        self.patch_button.setText(
            QCoreApplication.translate("MainWindow", "Patch", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.log_tab),
            QCoreApplication.translate("MainWindow", "Log", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.skin_tab),
            QCoreApplication.translate("MainWindow", "Skin", None),
        )

    # retranslateUi
