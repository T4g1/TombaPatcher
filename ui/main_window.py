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
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(947, 796)
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

        self.patch_layout = QHBoxLayout()
        self.patch_layout.setObjectName("patch_layout")
        self.advanced_button = QPushButton(self.centralwidget)
        self.advanced_button.setObjectName("advanced_button")

        self.patch_layout.addWidget(self.advanced_button)

        self.advanced_layout = QHBoxLayout()
        self.advanced_layout.setObjectName("advanced_layout")
        self.extract_button = QPushButton(self.centralwidget)
        self.extract_button.setObjectName("extract_button")

        self.advanced_layout.addWidget(self.extract_button)

        self.apply_mods_button = QPushButton(self.centralwidget)
        self.apply_mods_button.setObjectName("apply_mods_button")

        self.advanced_layout.addWidget(self.apply_mods_button)

        self.compile_button = QPushButton(self.centralwidget)
        self.compile_button.setObjectName("compile_button")
        self.compile_button.setEnabled(True)

        self.advanced_layout.addWidget(self.compile_button)

        self.patch_layout.addLayout(self.advanced_layout)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.patch_layout.addItem(self.horizontalSpacer)

        self.patch_button = QPushButton(self.centralwidget)
        self.patch_button.setObjectName("patch_button")

        self.patch_layout.addWidget(self.patch_button)

        self.verticalLayout_2.addLayout(self.patch_layout)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setEnabled(True)
        self.mods_tab = QWidget()
        self.mods_tab.setObjectName("mods_tab")
        self.verticalLayout_3 = QVBoxLayout(self.mods_tab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setObjectName("actions_layout")
        self.refresh_mod_list = QPushButton(self.mods_tab)
        self.refresh_mod_list.setObjectName("refresh_mod_list")

        self.actions_layout.addWidget(self.refresh_mod_list)

        self.verticalLayout_3.addLayout(self.actions_layout)

        self.mod_list = QListWidget(self.mods_tab)
        self.mod_list.setObjectName("mod_list")

        self.verticalLayout_3.addWidget(self.mod_list)

        self.tabWidget.addTab(self.mods_tab, "")
        self.log_tab = QWidget()
        self.log_tab.setObjectName("log_tab")
        self.verticalLayout = QVBoxLayout(self.log_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.log = QPlainTextEdit(self.log_tab)
        self.log.setObjectName("log")

        self.verticalLayout.addWidget(self.log)

        self.tabWidget.addTab(self.log_tab, "")
        self.skin_tab = QWidget()
        self.skin_tab.setObjectName("skin_tab")
        self.skin_tab.setEnabled(True)
        self.horizontalLayout_3 = QHBoxLayout(self.skin_tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget.addTab(self.skin_tab, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 947, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)

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
        self.advanced_button.setText(
            QCoreApplication.translate("MainWindow", "Advanced...", None)
        )
        self.extract_button.setText(
            QCoreApplication.translate("MainWindow", "Extract", None)
        )
        self.apply_mods_button.setText(
            QCoreApplication.translate("MainWindow", "Apply mods", None)
        )
        self.compile_button.setText(
            QCoreApplication.translate("MainWindow", "Compile", None)
        )
        self.patch_button.setText(
            QCoreApplication.translate("MainWindow", "Patch", None)
        )
        self.refresh_mod_list.setText(
            QCoreApplication.translate("MainWindow", "Refresh", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.mods_tab),
            QCoreApplication.translate("MainWindow", "Mods", None),
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
