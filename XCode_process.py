# -*- coding: utf-8 -*-
"""
Created on Wed May 16

@author: rg

XCode.py mit pyqt5
Variante mit start eines separaten Porcesses für den TransCode
angeregt durch start_process.py und ProcessTest.py


"""

# import PyQt5.QtWidgets # Import the PyQt5 module we'll need
from PyQt5.QtWidgets import (QMainWindow, 
                             QTextEdit, 
                             QTableWidget,QTableWidgetItem,
#                             QComboBox,
                             QHeaderView,
#                             QFileDialog,
                             QLabel, 
                             QLineEdit, 
                             QPushButton,
#                             QRadioButton,
#                             QCheckBox,
                             QWidget,
                             QHBoxLayout, 
                             QVBoxLayout, 
#                             QGroupBox,
#                             QButtonGroup,
                             QApplication, 
                             QMessageBox)

from PyQt5.QtCore import QProcess, QObject
from PyQt5.QtGui import QTextCursor, QColor

from math import log as logarit
from timeit import default_timer as timer
import datetime
import logger
import sys
import shutil
import os
# from subprocess import Popen, CREATE_NEW_CONSOLE

import XCodeUI # Hauptfenster; mit pyuic aus der UI-Datei konvertiert

class tsEintrag:
    def __init__(self, nr, fullpath, name, status):
        self.nr = nr
        self.fullpath = fullpath
        self.name = name
        self.status = status
    
    def __str__(self):
        return "{0}: {1} mit Status {2}".format(self.nr, self.fullpath, self.status)
    

class XCodeApp(QMainWindow, XCodeUI.Ui_MainWindow):
    def __init__(self):               
        super(self.__class__, self).__init__()
        
        self.setupUi(self)  # This is defined in XCodeUI.py file automatically
                            # It sets up layout and widgets that are defined
        # Instanz-Variablen
        self.process = None
        self.quelle  = "C:\\ts\\"
        self.ziel    = "E:\\Filme\\schnitt\\"
        self.logpath = "E:\\Filme\\log\\"
        self.tsliste = []       # Liste der ts-Objekte
        self.running = False    # im Prozess aktiv
        self.stopNext = False   # HalteSignal
        self.Zeile = 0          # aktuelle Zeile (0 - (n-1))
        self.incr = 0.0         # Increment des Procbar1
        self.pbarpos = 0        # Pos des PorcBar1
        self.prstart = 0        # start timer des prozesses
        self.prend = 0          # end timer
        self.ts_von = ""        # aktuelle quelle
        self.ts_nach = ""       # aktuelles ziel

        # Feintuning der Widgets
        self.tbl_files.setHorizontalHeaderLabels(('Nr', 'Status', 'Datei'))
        self.tbl_files.setAlternatingRowColors(True)
        header = self.tbl_files.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.edit.setReadOnly(True)
        # self.edit.LineWrapMode = QTextEdit.NoWrap
        self.edit.setTextBackgroundColor (QColor("lightyellow"))
        self.edit.setStyleSheet("background-color: lightyellow;")
        # self.edit.width = 400
        # self.edit.setAcceptRichText(True)
        self.edit.setWindowTitle("Prozess-Ausgabe")
        self.edit.setText("")
        
        self.led_pfad.setDisabled(True)
        self.probar1.setValue(0)
        self.probar2.setValue(0)
                
        # connects
        self.btn_ende.clicked.connect(self.progende)
        self.btn_start.clicked.connect(self.convert)
        
        # Abschluss Init; laden der Daten
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log = logger.logFile(self.logpath + "XCode_"+ self.dt + ".log", TimeStamp=True, printout=False)

        self.anzahl = self.ladeFiles(self.quelle)
        self.statusbar.showMessage("{0} Dateien geladen!".format(self.anzahl))
        if self.anzahl == 0:
            reply = QMessageBox.information( self, "Hinweis",
            "Es gibt im Order {0} keine ts-Dateien.\nNichts zu tun!".format(self.quelle))
            return
        else:
            self.incr = 100.0 / self.anzahl
        
    # Slots
    def StartProcess(self, cmd):
        self.process=QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.onReadData)        
        self.process.start(cmd)
        
    def onReadData(self):
        txt = self.process.readAllStandardOutput().data().decode('cp850')
        self.edit.append(txt)
        self.edit.moveCursor(QTextCursor.End)
        # print("got data!")

    def onFinished(self,  exitCode,  exitStatus):
        self.prend = timer()
        self.running = False
        # print("Vorbei")
        m, s = divmod(self.prend - self.prstart, 60)
        h, m = divmod(m, 60)
        time_str = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h, m, s)     
        Datei = self.tsliste[self.Zeile]
        
        # print("Finished; exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
        if exitStatus == 0:
            if exitCode == 0:
                qlen = os.stat(self.ts_von).st_size
                try:
                    zlen = os.stat(self.ts_nach).st_size
                except:
                    zlen = 0    
                self.log.log("{0} --> {1} ({2:2.2f}%)".format(format_size(qlen), format_size(zlen), zlen / qlen * 100))
                self.log.log("Dauer: {0}; ReturnCode: {1}".format(time_str, exitCode))
                self.log.log("OK")
                shutil.move(self.ts_von, self.ts_von + ".done")
                Datei.status = "OK" 
                # self.tbl_files.setItem(self.Zeile, 1, QTableWidgetItem("OK"))                
            else:
                self.log.log("Fehler! ReturnCode: {0}".format(exitCode))            
                Datei.status = "Fehler ({0})".format(exitCode)                
                # self.tbl_files.setItem(self.Zeile, 1, QTableWidgetItem("Fehler ({0})".format(exitCode)))                
        else:
            self.log.log("Fehler! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))            
            Datei.status = "Fehler {0} / {1}".format(exitCode, exitStatus)
#            self.tbl_files.setItem(self.Zeile, 1, QTableWidgetItem("RUN-Fehler ({0})".format(exitStatus)))
          
        # Abschluss-Arbeiten des aktuellen Prozesses
        self.edit.setText(" ")
        self.refreshTable(False)     
        self.process = None
        self.probar2.setRange(0,1)  # stopt hin-her   
            
        # weitermachen oder aufhören
        if self.stopNext:
                self.ende_verarbeitung()
                return            
        if self.Zeile < self.anzahl - 1:            
            self.Zeile +=1
            self.convert()
        else:
            self.ende_verarbeitung()

    def ladeFiles(self, ts_pfad):     # lädt die ts-Files
        # Liste der ts-files laden
        i = 0
        for entry in os.scandir(ts_pfad):
            if entry.is_file():               
                if entry.name[-3:] == ".ts":
                    i += 1
                    sz = os.path.join(ts_pfad, entry.name)
                    tse = tsEintrag(i, sz, entry.name, "waiting...")
                    self.tsliste.append(tse)
                    self.log.log("Lade: {0:2}: {1}".format(i, entry.name))
        
        self.refreshTable(True)
        return len(self.tsliste)

    def refreshTable(self, neuaufbau):
        # das Table-widget füllen
        if neuaufbau:
            self.tbl_files.setRowCount(0)
        for nr, ts in enumerate(self.tsliste):
            if neuaufbau:
                self.tbl_files.insertRow(nr)
            self.tbl_files.setItem(nr, 0, QTableWidgetItem(str(ts.nr)))
            self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.status))  
            self.tbl_files.setItem(nr, 2, QTableWidgetItem(ts.name))
        if neuaufbau:
            self.tbl_files.selectRow(0)
                    
    def convert(self):
        '''
        konvertiert eine ts-Datei über einen separaten Prozess
        die aktuelle Zeile wird als Instanzvariable erwartet
        '''
        self.pbarpos += self.incr
        self.probar1.setValue(self.pbarpos)
        self.probar2.setRange(0,0)  # start hin-her
        # self.probar2.setValue(0)
        self.btn_start.setEnabled(False)

        row = self.Zeile
        Datei = self.tsliste[row]
            
        Datei.status = "running..."
        self.refreshTable(False)
        self.tbl_files.selectRow(row)
        self.ts_nach = self.ziel + Datei.name[:-3] + ".mkv"
        self.ts_von = Datei.fullpath
        self.log.log("\nStart Konvertierung von {0} . . .".format(self.ts_von))
        self.probar1.setValue(self.pbarpos)
        self.xcode(self.ts_von, self.ts_nach)

    def xcode(self, von, nach):
        # montieren des cmd-Befehls, um ffmpeg zu starten
        cmd = "cmd /C c:\\ffmpeg\\bin\\ffmpeg -i"
        cmd = cmd + ' "{0}"'.format(von)
        #cmd = cmd + ' -map 0:v -map 0:a:0 -c:v h264_nvenc -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska '
        cmd = cmd + ' -map 0 -c:v h264_nvenc -c:a copy -sn -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska -y '
        cmd = cmd + '"{0}"'.format(nach)
        self.log.log("ffmpeg Aufruf: {0}".format(cmd))
        self.edit.setText(cmd)
        self.statusbar.showMessage("Umwandlung {0} -> {1}".format(von, nach))
        self.prstart = timer()
        # Prozess lostreten
        self.running = True
        self.process=QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.onReadData)        
        self.process.start(cmd)
           

    def progende(self):     # Ende Proc mit Nachfrage
        if self.running:
            reply = QMessageBox.question( self, "Nachfrage",
            "Ablauf abbrechen?\nDas wird nach dem Ende der aktuellen Konvertierung geschehen!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.stopNext = True
                self.statusbar.showMessage("Die Konverierung endet nach dem aktuellen Porzess!")
                self.btn_ende.setText("Abbruch angefordert!")
                self.btn_ende.setDisabled(True)
        else:
            self.ende_verarbeitung()
        
    def ende_verarbeitung(self):
        self.tbl_files.selectRow(-1)
        self.log.log("-" * 80)
        self.running = False
        self.statusbar.showMessage("Verarbeitung beendet!")
        self.log.log("Ende!")
        self.log.close()
        self.close()

def format_size(flen: int):
        """Human friendly file size"""
        unit_list = list(zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 3, 3, 3, 3, 3]))
        if flen > 1:
            exponent = min(int(logarit(flen, 1024)), len(unit_list) - 1)
            quotient = float(flen) / 1024 ** exponent
            unit, num_decimals = unit_list[exponent]
            s = '{:{width}.{prec}f} {}'.format(quotient, unit, width=8, prec=num_decimals )
            s = s.replace(".", ",")
            return s
        elif flen == 1:
            return '  1 byte'
        else: # flen == 0
            return ' 0 bytes'


def main():
    app = QApplication(sys.argv)  # A new instance of QApplication
    form = XCodeApp()              # We set the form to be our ExampleApp (design)
    if form.anzahl == 0:          # nix zu tun!
        return
    form.show()                    # Show the form
    app.exec_()                    # and execute the app


if __name__ == '__main__':        # if we're running file directly and not importing it
    main()                        # run the main function