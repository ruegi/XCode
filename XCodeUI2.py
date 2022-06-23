# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'XCodeUI2.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(817, 728)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("XC.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.lbl_pfad = QtWidgets.QLabel(self.centralwidget)
        self.lbl_pfad.setObjectName("lbl_pfad")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lbl_pfad)
        self.le_pfad = QtWidgets.QLineEdit(self.centralwidget)
        self.le_pfad.setObjectName("le_pfad")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.le_pfad)
        self.lbl_tsfiles = QtWidgets.QLabel(self.centralwidget)
        self.lbl_tsfiles.setObjectName("lbl_tsfiles")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.lbl_tsfiles)
        self.tbl_files = QtWidgets.QTableWidget(self.centralwidget)
        self.tbl_files.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl_files.sizePolicy().hasHeightForWidth())
        self.tbl_files.setSizePolicy(sizePolicy)
        self.tbl_files.setMinimumSize(QtCore.QSize(0, 520))
        self.tbl_files.setStyleSheet("QProgressBar {\n"
"    border: 2px solid #2196F3;\n"
"    border-radius: 5px;\n"
"    background-color: #E0E0E0;\n"
"    text-align: center\n"
"}\n"
"QProgressBar::chunk {\n"
"    background-color: #2196F3;\n"
"}")
        self.tbl_files.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_files.setCornerButtonEnabled(True)
        self.tbl_files.setRowCount(5)
        self.tbl_files.setColumnCount(6)
        self.tbl_files.setObjectName("tbl_files")
        self.tbl_files.verticalHeader().setVisible(False)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.tbl_files)
        self.lbl_fortschritt = QtWidgets.QLabel(self.centralwidget)
        self.lbl_fortschritt.setObjectName("lbl_fortschritt")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.lbl_fortschritt)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.probar2 = QtWidgets.QProgressBar(self.centralwidget)
        self.probar2.setMaximum(1)
        self.probar2.setProperty("value", 0)
        self.probar2.setTextVisible(False)
        self.probar2.setFormat("")
        self.probar2.setObjectName("probar2")
        self.horizontalLayout_3.addWidget(self.probar2, 0, QtCore.Qt.AlignLeft)
        self.probar1 = QtWidgets.QProgressBar(self.centralwidget)
        self.probar1.setProperty("value", 0)
        self.probar1.setObjectName("probar1")
        self.horizontalLayout_3.addWidget(self.probar1)
        self.formLayout.setLayout(9, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.horizontalLayout.addItem(spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btn_ende = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_ende.sizePolicy().hasHeightForWidth())
        self.btn_ende.setSizePolicy(sizePolicy)
        self.btn_ende.setObjectName("btn_ende")
        self.horizontalLayout.addWidget(self.btn_ende)
        self.btn_start = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_start.sizePolicy().hasHeightForWidth())
        self.btn_start.setSizePolicy(sizePolicy)
        self.btn_start.setMinimumSize(QtCore.QSize(0, 40))
        self.btn_start.setAutoDefault(True)
        self.btn_start.setFlat(False)
        self.btn_start.setObjectName("btn_start")
        self.horizontalLayout.addWidget(self.btn_start)
        self.formLayout.setLayout(11, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.lbl_version = QtWidgets.QLabel(self.centralwidget)
        self.lbl_version.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lbl_version.setAutoFillBackground(True)
        self.lbl_version.setObjectName("lbl_version")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole, self.lbl_version)
        self.verticalLayout.addLayout(self.formLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.statusbar.setFont(font)
        self.statusbar.setSizeGripEnabled(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "XCode  (*.ts   -->  *.mkv) "))
        self.lbl_pfad.setText(_translate("MainWindow", "Pfad der TS-Dateien:"))
        self.le_pfad.setText(_translate("MainWindow", "C:\\ts"))
        self.le_pfad.setPlaceholderText(_translate("MainWindow", "Pfad zu den ts-Videos"))
        self.lbl_tsfiles.setText(_translate("MainWindow", "TS-Dateien"))
        self.lbl_fortschritt.setText(_translate("MainWindow", "Gesamt-Fortschritt"))
        self.btn_ende.setText(_translate("MainWindow", "Ende"))
        self.btn_start.setText(_translate("MainWindow", "Start"))
        self.lbl_version.setText(_translate("MainWindow", "Version 0.0 vom 00.00.2021"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
