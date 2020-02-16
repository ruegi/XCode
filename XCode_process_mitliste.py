# -*- coding: utf-8 -*-
"""
Created on Wed May 16

@author: rg

XCode.py mit pyqt5
Variante mit start eines separaten Porcesses für den TransCode
angeregt durch start_process.py und ProcessTest.py


"""
from PyQt5.QtWidgets import (QMainWindow,
                             QTextEdit, 
                             QTableWidget,
                             QTableWidgetItem,
                             QHeaderView,
                             QLabel,
                             QLineEdit, 
                             QPushButton,
                             QWidget,
                             QHBoxLayout, 
                             QVBoxLayout, 
                             QApplication,
                             QMessageBox)

from PyQt5.QtCore import QProcess, QObject
from PyQt5.QtGui import QTextCursor, QColor, QIcon

from math import log as logarit
from timeit import default_timer as timer
import datetime
import logger
import sys
import shutil
import os
import ffcmd

import liste as liste  # hält eine Liste der umzuwandelnden Dateien

import XCodeUI # Hauptfenster; mit pyuic aus der UI-Datei konvertiert

class Konstanten:                       # Konstanten des Programms
    quelle  = "C:\\ts\\"
    ziel    = "E:\\Filme\\schnitt\\"
    logpath = "E:\\Filme\\log\\"

class tsEintrag:
    def __init__(self, nr, fullpath, name, status):
        self.nr = nr
        self.fullpath = fullpath
        self.name = name
        self.status = status
    
    def __str__(self):
        return "{0}: {1} mit Status {2}".format(self.nr, self.fullpath, self.status)

    def setStatus(self, status):
        self.status = status

class XCodeApp(QMainWindow, XCodeUI.Ui_MainWindow):
    def __init__(self):               
        super(self.__class__, self).__init__()
        
        self.setupUi(self)  # This is defined in XCodeUI.py file automatically
                            # It sets up layout and widgets that are defined

        # Instanz-Variablen
        self.ff = ffcmd.ffmpegcmd()
        self.process = None
        self.processkilled = False
        self.quelle  = Konstanten.quelle
        self.ziel    = Konstanten.ziel
        self.logpath = Konstanten.logpath
        self.tsliste = liste.liste()  # Liste der ts-Objekte
        self.running = False    # im Prozess aktiv
        self.stopNext = False   # HalteSignal
#        self.Zeile = 0         # aktuelle Zeile (0 - (n-1))
        self.incr = 0.0         # Increment des Procbar1
        self.pbarpos = 0        # Pos des PorcBar1
        self.prstart = 0        # start timer des prozesses
        self.prend = 0          # end timer
        self.ts_von = ""        # aktuelle quelle
        self.ts_nach = ""       # aktuelles ziel
        self.lastcmd = ""       # letzter cmd, der im Prozess verarbeitet wurde

        # Icon versorgen
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'XC.ico'))

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


        self.log.log("Umwandlung mit:")
        self.log.log(self.ff.ffXcodeCmd("{EingabeDatei}", "{AusgabeDatei}", nurLog=True) + "\n")

        self.ladeFiles(self.quelle)

        if self.tsliste.size == 0:
            reply = QMessageBox.information( self, "Hinweis",
            "Es gibt im Order {0} keine ts-Dateien.\nNichts zu tun!".format(self.quelle))
            return
        else:
            self.incr = 100.0 / self.tsliste.size
        self.statusbar.showMessage("{0} Dateien geladen!".format(self.tsliste.size))

    # Slots
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
        Datei = self.tsliste.lastObj
        
        # print("Finished; exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
        if exitStatus == 0:
            if exitCode == 0:   # Abschluss-Verarbeitung, wenn alles gut gelaufen ist
                qlen = os.stat(self.ts_von).st_size
                try:
                    zlen = os.stat(self.ts_nach).st_size
                except:
                    zlen = 0    
                self.log.log("{0} --> {1} ({2:2.2f}%)".format(format_size(qlen), format_size(zlen), zlen / qlen * 100))
                self.log.log("Dauer: {0}; ReturnCode: {1}".format(time_str, exitCode))
                self.log.log("OK")
                shutil.move(Datei.fullpath, Datei.fullpath + ".done")
                Datei.setStatus("OK")
            else:       # Abschluss-Verarbeitung bei Fehler
                self.log.log("Fehler! ReturnCode: {0}".format(exitCode))
                self.log.log("Letzter Befehl:\n{0}".format(self.lastcmd))
                Datei.setStatus("Fehler ({0})".format(exitCode))
        else:
            Datei.setStatus("Fehler {0} / {1}".format(exitCode, exitStatus))
            if self.processkilled:
                self.log.log("Harter Abbruch! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
                return  # keine weitere Verarbeitung
            else:
                self.log.log("Fehler! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))

        # Abschluss-Arbeiten des aktuellen Prozesses
        self.edit.setText(" ")
        self.refreshTable(False)     
        self.process = None
        self.probar2.setRange(0,1)  # stoppt hin-her
            
        # weitermachen oder aufhören
        if self.stopNext:   # sofort aufhören
                self.ende_verarbeitung()
                return            
        if self.tsliste.findNext() is None:
            self.ende_verarbeitung()    # fertig
        else:
            self.convert()              # nächste Datei

    def closeEvent(self, event):
        if self.running:
            if self.stopNext:
                reply = QMessageBox.warning(self, "Achtung!",
                                             "Laufende Konvertierung abbrechen?\nDas macht die neu erzeugte Ausgabe unbrauchbar!",
                                             QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # Abbrechen!
                    self.processkilled = True
                    self.ende_verarbeitung()
                    event.accept()
                else:
                    self.processkilled = False
                    event.ignore()  # hier kein weiterer close (wegen self.running)!
        else:
            event.accept()  # OK, Schluss jetzt

    # Funktionen
    def ladeFiles(self, ts_pfad):     # lädt die ts-Files
        # Liste der ts-files laden
        i = 0
        for entry in os.scandir(ts_pfad):
            if entry.is_file():
                fname, fext = os.path.splitext(entry.name)
                if fext in [".ts", ".mpg", ".mp4", ".mkv", ".mv4", ".mpeg", ".avi"]:
                    i += 1
                    fullpath = os.path.join(ts_pfad, entry.name)
                    tse = tsEintrag(i, fullpath, entry.name, "waiting...  ")
                    self.tsliste.append(tse)
                    self.log.log("Lade: {0:2}: {1}".format(i, entry.name))
        self.tsliste.findFirst()
        self.refreshTable(True)
        return self.tsliste.size

    def refreshTable(self, neuaufbau):
        # das Table-widget füllen
        if neuaufbau:
            self.tbl_files.setRowCount(0)
        for ts in self.tsliste.liste:
            # print(ts)
            # direkte Benutzung der tsliste, ohne die Werte von lastPos und lastObj zu verändern
            nr = ts.nr - 1
            if neuaufbau:
                self.tbl_files.insertRow(nr)
            self.tbl_files.setItem(nr, 0, QTableWidgetItem(str(ts.nr)))
            self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.status))
            self.tbl_files.setItem(nr, 2, QTableWidgetItem(ts.name))
        self.tbl_files.selectRow(self.tsliste.lastPos)

    def convert(self):
        '''
        konvertiert eine ts-Datei über einen separaten Prozess
        '''
        # GUI anpassen
        self.pbarpos += self.incr
        self.probar1.setValue(round(self.pbarpos))
        self.probar2.setRange(0,0)  # start hin-her
        # self.probar2.setValue(0)
        self.btn_start.setEnabled(False)

        row = self.tsliste.lastPos
        Datei = self.tsliste.lastObj
            
        Datei.setStatus("running...")
        self.refreshTable(False)
        self.tbl_files.selectRow(row)
        fname, fext = os.path.splitext(Datei.name)
        self.ts_nach = self.ziel + fname + ".mkv"
        self.ts_von = Datei.fullpath
        self.log.log("\nStart Konvertierung von {0} . . .".format(self.ts_von))

        # cmd montieren        
        self.lastcmd = self.ff.ffXcodeCmd(self.ts_von, self.ts_nach)
        self.log.log("ffmpeg Aufruf: {0}".format(self.lastcmd))
        self.statusbar.showMessage("Umwandlung {0} -> {1}".format(self.ts_von, self.ts_nach))
        self.prstart = timer()

        # Prozess starten
        self.running = True
        self.process=QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.onReadData)        
        self.process.start(self.lastcmd)

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
        if self.btn_start.isEnabled():
            self.log.log("Nichts getan!")
        else:
            if self.processkilled:
                self.process.kill()
                self.process.waitForFinished(5000)
                if os.path.isfile(self.ts_nach):    #die defekte Datei löschen
                    try:  # versuchen, die kaputte *.mkv"-datei zu löschen
                        os.remove(self.ts_nach)
                    except:
                        QMessageBox.information(self, "Achtung!",
                                                "Die defekte Datei \n{0}\nkonnte NICHT gelöscht werden!".format(
                                                    self.ts_nach))
                        self.log.log("Defekte Zieldatei [{0}] konnte NICHT gelöscht werden!")
                    else:
                        self.log.log("Defekte Zieldatei wurde gelöscht!")
                self.log.log("Harter Abbruch!")
                txt = "Harter Abbruch!"
            elif self.stopNext:
                txt = "Die Verarbeitung wurde nach Anforderung vorzeitig beendet!"
                self.log.log("Ende nach Abbruch!" )
            else:
                txt = "Programm-Ende!"
                self.log.log("Ende!")
            erg, isOK = self.findeErgebnis()
            if isOK:
                QMessageBox.information(self, "JobEnde", txt + "\n" + erg)
            else:
                if self.processkilled:
                    pass
                else:
                    QMessageBox.warning(self, "JobEnde", txt + "\n" + erg)
            self.log.log(erg)
        self.log.close()
        self.running = False
        self.close()

    def findeErgebnis(self):
        wait = 0
        ok = 0
        err = 0
        for ts in self.tsliste.liste:
            if ts.status == "OK":
                ok += 1
            elif ts.status == "waiting...  ":
                wait += 1
            else:
                err +=1
        if (wait == 0) & (err == 0) & (ok > 0):
            txt = "\nAlles OK!\n\nOK: {0}\n".format(ok) + "Fehler: {0}\n".format(err) + "Nicht bearbeitet: {0}\n".format(wait)
            isOK = True
        else:
            txt = "\nErgebnis\n\nOK: {0}\n".format(ok) + "Fehler: {0}\n".format(err) + "Nicht bearbeitet: {0}\n".format(wait)
            isOK = False
        return (txt, isOK)


def ffmpegBefehl(ts_von, ts_nach):
        # das "&" stört im Aufruf, es muss maskiert werden
        von = ts_von.replace("&", "^&")
        nach = ts_nach.replace("&", "^&")
        cmd = "c:\\ffmpeg\\bin\\ffmpeg -i "
        cmd = cmd + "\"{0}\" ".format(ts_von)
        #cmd = cmd + ' -map 0:v -map 0:a:0 -c:v h264_nvenc -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska '
        # cmd = cmd + '-c:v h264_nvenc -c:a copy -c:s copy -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska -y '
        # die folgenden Parameter haben die Eigenschaften (2018-12-13):
        #  - gute Videoqualität per nvenc;
        #  - alle Audios werden kopiert
        #  - Deutscher Untertitel wirde als dvdsub einkopiert
        #cmd = cmd + '-map 0 -c:v h264_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset fast -f matroska -y '
        cmd = cmd + '-map 0 -c:v hevc_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset fast -f matroska -y '
        
        cmd = cmd + "\"{0}\"".format(ts_nach)
        return cmd

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
    form = XCodeApp()             # We set the form to be our ExampleApp (design)
    if form.tsliste.size == 0:    # nix zu tun!
        return
    form.show()                   # Show the form
    app.exec_()                   # and execute the app


if __name__ == '__main__':        # if we're running file directly and not importing it
    main()                        # run the main function