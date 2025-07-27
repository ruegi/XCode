# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'XCodeUI.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFormLayout, QHBoxLayout,
    QHeaderView, QLabel, QLayout, QLineEdit,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTableWidget, QTableWidgetItem,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 800)
        icon = QIcon()
        icon.addFile(u"XC.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.lbl_pfad = QLabel(self.centralwidget)
        self.lbl_pfad.setObjectName(u"lbl_pfad")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.lbl_pfad)

        self.led_pfad = QLineEdit(self.centralwidget)
        self.led_pfad.setObjectName(u"led_pfad")
        font = QFont()
        font.setFamilies([u"Cascadia Mono"])
        font.setPointSize(10)
        self.led_pfad.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.led_pfad)

        self.lbl_tsfiles = QLabel(self.centralwidget)
        self.lbl_tsfiles.setObjectName(u"lbl_tsfiles")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.lbl_tsfiles)

        self.tbl_files = QTableWidget(self.centralwidget)
        if (self.tbl_files.columnCount() < 6):
            self.tbl_files.setColumnCount(6)
        if (self.tbl_files.rowCount() < 5):
            self.tbl_files.setRowCount(5)
        self.tbl_files.setObjectName(u"tbl_files")
        self.tbl_files.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl_files.sizePolicy().hasHeightForWidth())
        self.tbl_files.setSizePolicy(sizePolicy)
        self.tbl_files.setMinimumSize(QSize(0, 300))
        self.tbl_files.setFont(font)
        self.tbl_files.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid #2196F3;\n"
"    border-radius: 5px;\n"
"    background-color: #E0E0E0;\n"
"    text-align: center\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #2196F3;\n"
"}")
        self.tbl_files.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_files.setCornerButtonEnabled(True)
        self.tbl_files.setRowCount(5)
        self.tbl_files.setColumnCount(6)
        self.tbl_files.verticalHeader().setVisible(False)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.tbl_files)

        self.lbl_command = QLabel(self.centralwidget)
        self.lbl_command.setObjectName(u"lbl_command")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.lbl_command)

        self.edit = QTextEdit(self.centralwidget)
        self.edit.setObjectName(u"edit")
        self.edit.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.edit.sizePolicy().hasHeightForWidth())
        self.edit.setSizePolicy(sizePolicy1)
        self.edit.setMinimumSize(QSize(0, 192))
        self.edit.setBaseSize(QSize(1147, 192))
        self.edit.setFont(font)
        self.edit.setFocusPolicy(Qt.NoFocus)
        self.edit.setAutoFillBackground(True)
        self.edit.setStyleSheet(u"")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.edit)

        self.lbl_fortschritt = QLabel(self.centralwidget)
        self.lbl_fortschritt.setObjectName(u"lbl_fortschritt")

        self.formLayout.setWidget(11, QFormLayout.LabelRole, self.lbl_fortschritt)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.probar2 = QProgressBar(self.centralwidget)
        self.probar2.setObjectName(u"probar2")
        self.probar2.setMaximum(1)
        self.probar2.setValue(0)
        self.probar2.setTextVisible(False)
        self.probar2.setFormat(u"")

        self.horizontalLayout_3.addWidget(self.probar2, 0, Qt.AlignLeft)

        self.probar1 = QProgressBar(self.centralwidget)
        self.probar1.setObjectName(u"probar1")
        font1 = QFont()
        font1.setFamilies([u"Cascadia Mono"])
        self.probar1.setFont(font1)
        self.probar1.setValue(0)

        self.horizontalLayout_3.addWidget(self.probar1)


        self.formLayout.setLayout(11, QFormLayout.FieldRole, self.horizontalLayout_3)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.horizontalLayout.addItem(self.verticalSpacer)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btn_ende = QPushButton(self.centralwidget)
        self.btn_ende.setObjectName(u"btn_ende")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_ende.sizePolicy().hasHeightForWidth())
        self.btn_ende.setSizePolicy(sizePolicy2)
        self.btn_ende.setMinimumSize(QSize(75, 0))
        self.btn_ende.setMaximumSize(QSize(16777215, 40))
        self.btn_ende.setBaseSize(QSize(75, 40))
        font2 = QFont()
        font2.setPointSize(11)
        self.btn_ende.setFont(font2)

        self.horizontalLayout.addWidget(self.btn_ende)

        self.btn_start = QPushButton(self.centralwidget)
        self.btn_start.setObjectName(u"btn_start")
        sizePolicy2.setHeightForWidth(self.btn_start.sizePolicy().hasHeightForWidth())
        self.btn_start.setSizePolicy(sizePolicy2)
        self.btn_start.setMinimumSize(QSize(75, 40))
        self.btn_start.setMaximumSize(QSize(16777215, 40))
        self.btn_start.setBaseSize(QSize(75, 40))
        self.btn_start.setFont(font2)
        self.btn_start.setAutoDefault(True)
        self.btn_start.setFlat(False)

        self.horizontalLayout.addWidget(self.btn_start)


        self.formLayout.setLayout(13, QFormLayout.FieldRole, self.horizontalLayout)

        self.lbl_version = QLabel(self.centralwidget)
        self.lbl_version.setObjectName(u"lbl_version")
        self.lbl_version.setLayoutDirection(Qt.RightToLeft)
        self.lbl_version.setAutoFillBackground(True)

        self.formLayout.setWidget(14, QFormLayout.FieldRole, self.lbl_version)

        self.lbl_frames = QLabel(self.centralwidget)
        self.lbl_frames.setObjectName(u"lbl_frames")
        font3 = QFont()
        font3.setFamilies([u"Cascadia Mono"])
        font3.setPointSize(10)
        font3.setBold(True)
        self.lbl_frames.setFont(font3)

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.lbl_frames)


        self.verticalLayout.addLayout(self.formLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font4 = QFont()
        font4.setBold(True)
        self.statusbar.setFont(font4)
        self.statusbar.setSizeGripEnabled(True)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"XCode  (*.ts   -->  *.mkv) ", None))
        self.lbl_pfad.setText(QCoreApplication.translate("MainWindow", u"Pfad der TS-Dateien:", None))
        self.led_pfad.setText(QCoreApplication.translate("MainWindow", u"C:\\ts", None))
        self.led_pfad.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Pfad zu den ts-Videos", None))
        self.lbl_tsfiles.setText(QCoreApplication.translate("MainWindow", u"TS-Dateien", None))
        self.lbl_command.setText(QCoreApplication.translate("MainWindow", u"Prozess-Ausgabe", None))
        self.edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Prozess-Ausgabe", None))
        self.lbl_fortschritt.setText(QCoreApplication.translate("MainWindow", u"Fortschritt", None))
        self.btn_ende.setText(QCoreApplication.translate("MainWindow", u"Ende", None))
        self.btn_start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.lbl_version.setText(QCoreApplication.translate("MainWindow", u"Version 0.0 vom 00.00.2021", None))
        self.lbl_frames.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

