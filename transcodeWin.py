# -*- coding: utf-8 -*-
"""
Created on 2021-07-27

@author: rg

Hauptprogramm mit pyqt5

Dieses Window transcodiert ein Video in ein HEVC-MKV mit Hilfe von ffmpeg und einer ffcmd.ini

"""
from PyQt5.QtWidgets import (QMainWindow, 
                             QLabel, 
                             QLineEdit, 
                             QPushButton,
                             QWidget,
                             QApplication, 
                             QMessageBox)

from PyQt5.QtGui import QIcon       # QTextCursor, QColor,
from PyQt5.QtCore import Qt         # QProcess, QObject, 

import sys
import os
import subprocess


import transcodeWinUI # Hauptfenster; mit pyuic aus der UI-Datei konvertiert

# Handle high resolution displays (thx 2 https://stackoverflow.com/questions/43904594/pyqt-adjusting-for-different-screen-resolution):
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# einige statische Konstanten
class Konstanten():
    FFMPEG = r'c:\ffmpeg\bin\ffmpeg.exe'
    ICON = 'XCode.ico'

class mainApp(QMainWindow, transcodeWinUI.Ui_MainWindow):
    def __init__(self):               
        super(self.__class__, self).__init__()
        
        self.setupUi(self)  # This is defined in ...UI.py file automatically
                            # It sets up layout and widgets that are defined
        # Instanz-Variablen

        # Icon versorgen
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + Konstanten.ICON))

        # # Feintuning der Widgets
        # self.cbGruppen.addItem("ohne")

        # connects
        self.btn_stop.clicked.connect(self.progende)        
        # self.leName.installEventFilter(self)  # Eventfilter wie FocusIn und Out montieren
        self.btn_start.
        self.btn_stop.setFocus()
        
        self.show()                   # Show the form

        
    # Slots
    # def eventFilter(self, source, event):
    #     if (event.type() == QEvent.FocusOut and
    #         source is self.leName):
    #         # print('eventFilter: focus out')
    #         if self.grpLaden(self.leName.text()) > 0:
    #             self.leName.setFocus()
    #             return True
    #     return super(QMainWindow, self).eventFilter(source, event)

    def startjob(self):
        pass
                
    # Funktionen
    def progende(self):     # Ende Proc mit Nachfrage
        self.close()
   
    def Hinweis(self, nachricht ):        
        self.statusbar.showMessage(nachricht)        

        
def main():
    app = QApplication(sys.argv)  # A new instance of QApplication
    form = mainApp()              # We set the form to be our App (design)
    app.exec_()                   # and execute the app


if __name__ == '__main__':        # if we're running file directly and not importing it
    main()                        # run the main function