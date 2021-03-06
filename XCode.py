# -*- coding: utf-8 -*-
"""
Created on Wed May 16

@author: rg

XCode.py mit pyqt5
Variante mit start eines separaten Porcesses für den TransCode
angeregt durch start_process.py und ProcessTest.py

Versionen:
1.2     Änderung auf eine ini-Date- die nach SD, HD und FullHD differenziert,
        frame-Zeile in der Statuszeile
1.3     Info Typ als neue Spalte in der Tabelle;
        Fortschrittsbalken in der Spalte 'Status' der Tabelle

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
                             QMessageBox,
                             QStyledItemDelegate,
                             QStyleOptionProgressBar,
                             QStyle)

from PyQt5.QtCore import QProcess, QObject, Qt
from PyQt5.QtGui import QTextCursor, QColor, QIcon

from math import log as logarit
from timeit import default_timer as timer
import datetime
import logger
import sys
import shutil
import os
import ffcmd
from random import randint

from pymediainfo import MediaInfo

import liste.liste as liste  # hält eine Liste der umzuwandelnden Dateien

from pymediainfo import MediaInfo

import XCodeUI # Hauptfenster; mit pyuic aus der UI-Datei konvertiert

import transcodeWin

class Konstanten:                       # Konstanten des Programms
    QUELLE  = "C:\\ts\\"
    ZIEL    = "E:\\Filme\\schnitt\\"
    LOGPATH = "E:\\Filme\\log\\"
    VERSION = "1.3"
    VERSION_DAT = "2021-07-24"

class videoFile:
    def __init__(self, fullPathName, name, ext):
        self.fullPathName = fullPathName
        self.name = name
        self.ext = ext
        self.duration = 0   # FilmLänge in ms
        self.frameCount = 0
        self.fps = 0.0
        self.bitRate = 0
        self.weite = "1280"
        self.hoehe = "768"
        self.typ = "HD"
        self.getVideoDetails()

    def getVideoDetails(self):
        try:
            media_info = MediaInfo.parse(self.fullPathName)
            g_track = media_info.general_tracks[0]
            v_track = media_info.video_tracks[0]

            v_fr = v_track.frame_rate
            v_fc = v_track.frame_count
            v_br = v_track.bitrate
            g_du = g_track.duration
            # print("Video-FC =", v_fc)        
            self.fps = float(v_fr)
            self.weite = v_track.width
            iWeite  = int(self.weite)
            self.hoehe = v_track.height
            self.bitRate = v_track.bit_rate
            if self.bitRate is None:
                self.bitRate = 0
            self.duration = float(g_du)
            self.frameCount = int(self.duration / 1000 * self.fps + 0.5)
            if iWeite < 1280:
                self.typ = "SD"
                return
            elif iWeite < 1920:
                self.typ = "HD"
                return
            else:
                self.typ = "FullHD"
                return 
        except:            
            return
        

class tsEintrag:
    def __init__(self, nr, fullpath, name, ext, status):
        self.nr = nr
        self.X = "X"
        self.fullpath = fullpath
        self.name = name
        self.status = status
        self.progress = 0
        self.video = videoFile(fullpath, name, ext)
    
    def __str__(self):
        return "{0}: {1} mit Status {2}".format(self.nr, self.fullpath, self.status)

    def setStatus(self, status):
        self.status = status
    
    def toggleX(self):
        if self.status == "OK":
            return   # keine Änderung, da bereits fertig

        if self.X == "X":
            self.X = ""
            self.status = "-skip-"
        else:
            self.X = "X"
            self.status = "warten..."
        return

class jobControl():
    '''
    Diese Klasse beschreibt einen Tanscodier Job.
    alle Meldungen werden in einen Klassen-Lokalen Buffer geschrieben und bei JobEnde
    in die Logdatei transferiert    
    '''
    def __init__(self, nr, appObj, tsObj, ):
        self.nr = nr
        self.appObj = appObj
        self.tsObj = tsObj
        self.running = False
        self.start_time  = 0
        self.end_time = 0
        self.log_buffer = ""

    def onReadData(self):
        txt = self.process.readAllStandardOutput().data().decode('cp850')
        if txt.startswith("frame="):
            # self.statusbar.showMessage("> " + txt)  # alt; kein bei mehreren Jobs nicht mehr funktionieren
            data = txt.split("=")   # frame=344874 fps=136 q=20.0 Lsize= 3003827kB time=01:54:59.46 bitrate=3566.6kbits/s speed=2.72x
            txtAnzFr = data[1].strip().split(" ")
            try:
                anzFrames = int(txtAnzFr[0])
            except:
                anzFrames = 0
            if anzFrames > self.frameCount:
                anzFrames = self.frameCount
            # self.probar2.setValue(anzFrames)  # Anzeige der Position # alt; kein bei mehreren Jobs nicht mehr funktionieren
            # nur noch eigenen PorBar in der Tabelle versorgen
            pro = int(anzFrames/self.frameCount*100)
            row = self.tsliste.lastPos
            itm = self.appObj.tbl_files.item(row, 4)            
            itm.setData(Qt.UserRole+1000, pro)            
            self.appObj.tsliste.lastObj.progress = pro
            # print("txtAnzFr: ", txtAnzFr, " ,Frame:", anzFrames," von ", self.frameCount)
        else: 
            pass    # alt; kein bei mehreren Jobs nicht mehr funktionieren           
            # self.edit.append(txt)
            # self.edit.moveCursor(QTextCursor.End)        


class ProgressDelegate(QStyledItemDelegate):
    '''
    Mit der paint-Methode des Delegates können die Progress-Bars in der letzten Spalte konfiguriert werden
    Dabei taucht ein Problem auf:
    dieses Objekt hat keine Verbindung zu den anderen Objeten zu Laufzeit.
    Um den den aktuellen Fortschritt zu erhalten, muss dieser in diesem Zell-Item als User-Data hinterlegt werden.
    Das geschieht mit "index.data(Qt.UserRole+1000)" (beim lesen) und "setData(index.data(Qt.UserRole+1000), prozent)" beim schreiben.
    Noch kenne ich keinen Weg, die häßliche grüne Farbe des Chunk zu ändern ...
    rg, 2021-07-25
    '''
    def paint(self, painter, option, index):
        progress = index.data(Qt.UserRole+1000)
        if progress is None: progress = 0
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        # opt.color = QColor(200, 200, 0)
        opt.textAlignment = Qt.AlignCenter
        opt.minimum = 0
        opt.maximum = 100        
        opt.progress = progress
        opt.text = f"{progress}%"
        opt.textVisible = True
        QApplication.style().drawControl(QStyle.CE_ProgressBar, opt, painter)        


class XCodeApp(QMainWindow, XCodeUI.Ui_MainWindow):
    def __init__(self):               
        super(self.__class__, self).__init__()
        
        self.setupUi(self)  # This is defined in XCodeUI.py file automatically
                            # It sets up layout and widgets that are defined

        pbarsheet = '''
QProgressBar {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    text-align: center
}
QProgressBar::chunk {
    background-color: #2196F3;
}'''        

        # Instanz-Variablen
        self.ff = ffcmd.ffmpegcmd()
        self.frameCount = 0
        self.process = None
        self.processkilled = False
        self.quelle  = Konstanten.QUELLE
        self.ziel    = Konstanten.ZIEL
        self.logpath = Konstanten.LOGPATH
        self.tsliste = liste.liste()  # Liste der ts-Objekte
        self.running = False    # im Prozess aktiv
        self.stopNext = False   # HalteSignal
#        self.Zeile = 0         # aktuelle Zeile (0 - (n-1))
        self.incr = 0.0         # Increment des Procbar1
        self.pbarpos = 0        # Pos des ProcBar1
        self.prstart = 0        # start timer des prozesses
        self.prend = 0          # end timer
        self.ts_von = ""        # aktuelle quelle
        self.ts_nach = ""       # aktuelles ziel
        self.lastcmd = ""       # letzter cmd, der im Prozess verarbeitet wurde
        self.w = None           # externes Transcode Window

        # Icon versorgen
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'XC.ico'))

        # Feintuning der Widgets
        self.tbl_files.setHorizontalHeaderLabels(("Nr", 'X', 'Datei', 'Typ', 'Progress', 'Status'))
        self.tbl_files.setAlternatingRowColors(True)
        delegate = ProgressDelegate(self.tbl_files)
        self.tbl_files.setItemDelegateForColumn(4, delegate)
        # self.tbl_files.setStyleSheet(pbarsheet)

        header = self.tbl_files.horizontalHeader()  
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tbl_files.setAlternatingRowColors(True)

        self.lbl_version.setText( "XCode Version " + Konstanten.VERSION + " vom " + Konstanten.VERSION_DAT )
        
        self.edit.setTextColor(QColor("White"))
        cName = "darkCyan"
        self.edit.setTextBackgroundColor (QColor(cName))
        self.edit.setStyleSheet(f"background-color: {cName};")
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
        self.tbl_files.doubleClicked.connect(self.toggleX)
        
        # Abschluss Init; laden der Daten
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log = logger.logFile(self.logpath + "XCode_"+ self.dt + ".log", TimeStamp=True, printout=False)


        self.log.log("Umwandlung mit:")
        self.log.log(self.ff.ffXcodeCmd("{EingabeDatei}", "{AusgabeDatei}",  "", nurLog=True) + "\n")

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
        if txt.startswith("frame="):
            self.statusbar.showMessage("> " + txt)
            data = txt.split("=")   # frame=344874 fps=136 q=20.0 Lsize= 3003827kB time=01:54:59.46 bitrate=3566.6kbits/s speed=2.72x
            txtAnzFr = data[1].strip().split(" ")
            try:
                anzFrames = int(txtAnzFr[0])
            except:
                anzFrames = 0
            if anzFrames > self.frameCount:
                anzFrames = self.frameCount
            self.probar2.setValue(anzFrames)  # Anzeige der Position

            pro = int(anzFrames/self.frameCount*100)
            row = self.tsliste.lastPos
            itm = self.tbl_files.item(row, 4)            
            itm.setData(Qt.UserRole+1000, pro)            
            self.tsliste.lastObj.progress = pro
            # print("txtAnzFr: ", txtAnzFr, " ,Frame:", anzFrames," von ", self.frameCount)
        else:            
            self.edit.append(txt)
            self.edit.moveCursor(QTextCursor.End)        
 
    def toggleX(self):
        # zunächst die aktuelle Zeile finden        
        idx = self.tbl_files.selectedIndexes()[0]
        row = idx.row()
        Datei = self.tsliste.findRow(row)
        if Datei is None:
            return
        else:
            Datei.toggleX()
            self.refreshTable(False)    # kein neuaufbau
        return         

    def onFinished(self,  exitCode,  exitStatus):
        self.prend = timer()
        self.running = False
        self.w.wobinich.disconnect()
        # print("Vorbei")
        m, s = divmod(self.prend - self.prstart, 60)
        h, m = divmod(m, 60)
        time_str = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h, m, s)     
        Datei = self.tsliste.lastObj
        if not Datei.X == "X":
            self.log.log(f">>> {Datei.nr} - {Datei.name} übersprungen!" )
            if self.tsliste.findNext() is None:
                self.ende_verarbeitung()    # fertig
            else:
                self.convert()              # nächste Datei
                return

        # print("Finished; exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
        if exitStatus == 0:
            if exitCode == 0:   # Abschluss-Verarbeitung, wenn alles gut gelaufen ist
                qlen = os.stat(self.ts_von + ".done").st_size
                try:
                    zlen = os.stat(self.ts_nach).st_size
                except:
                    zlen = 0    
                self.log.log("{0} --> {1} ({2:2.2f}%)".format(format_size(qlen), format_size(zlen), zlen / qlen * 100))
                self.log.log("Dauer: {0}; ReturnCode: {1}".format(time_str, exitCode))
                self.log.log("OK")
                # try:
                #     shutil.move(Datei.fullpath, Datei.fullpath + ".done")
                # except:
                #     self.log.log("Warnung: Konnte die QuelleDatei nicht in *.done umbenennen!")
                
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
        # self.probar2.setRange(0,1)  # stoppt hin-her
        self.probar2.setValue(0)  # ende der Anzeige
            
        # weitermachen oder aufhören
        if self.stopNext:   # sofort aufhören
                self.ende_verarbeitung()
                return            

        # den Fortschrittsbalken abschließen
        row = self.tsliste.lastPos
        itm = self.tbl_files.item(row, 4)         
        itm.setData(Qt.UserRole+1000, 100)        
        self.tsliste.lastObj.progress = 100

        # neuen Satz aussuchen
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


    def receiver(self, zahl):
        # empfängt die Fortschrittszahlen des Subwindow
        # und zeigt den Fortschritt im Zeilen-Fortschritts-Balken an
        row = self.tsliste.lastPos
        itm = self.tbl_files.item(row, 4)            
        itm.setData(Qt.UserRole+1000, zahl)
        self.tsliste.lastObj.progress = zahl


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
                    tse = tsEintrag(i, fullpath, entry.name, fext, "warten...  ")
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
                self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.X))
                self.tbl_files.setItem(nr, 2, QTableWidgetItem(ts.name))
                self.tbl_files.setItem(nr, 3, QTableWidgetItem(ts.video.typ))            
                self.tbl_files.setItem(nr, 4, QTableWidgetItem(ts.progress))
                itm = self.tbl_files.item(nr, 4)
                itm.setData(Qt.UserRole+1000, 0) 
                self.tbl_files.setItem(nr, 5, QTableWidgetItem(ts.status))
                # zentrieren
                itm = self.tbl_files.item(nr, 0)
                itm.setTextAlignment(Qt.AlignCenter)
                itm = self.tbl_files.item(nr, 1)
                itm.setTextAlignment(Qt.AlignCenter)
                itm = self.tbl_files.item(nr, 3)
                itm.setTextAlignment(Qt.AlignCenter)
                itm = self.tbl_files.item(nr, 5)
                itm.setTextAlignment(Qt.AlignCenter)
            else:
                if nr == self.tsliste.lastPos:
                    self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.X))
                    itm = self.tbl_files.item(nr, 1)
                    itm.setTextAlignment(Qt.AlignCenter)
                    itm = self.tbl_files.item(nr, 4)
                    itm.setData(Qt.UserRole+1000, ts.progress)                     
                    self.tbl_files.setItem(nr, 5, QTableWidgetItem(ts.status))
                    itm = self.tbl_files.item(nr, 5)
                    itm.setTextAlignment(Qt.AlignCenter)
                    break


            # if ts.status == "OK":
            #     itm.text = "OK"
            # elif ts.status == "Waiting":
            #     itm.text = "Wait"
            # else:
            #     itm.text = "{}%".format(ts.progress)

        self.tbl_files.selectRow(self.tsliste.lastPos)

    def convert(self):
        '''
        konvertiert eine ts-Datei über einen separaten Prozess
        '''
        row = self.tsliste.lastPos
        Datei = self.tsliste.lastObj
        # keine Verarbeitung, falls kein X gesetzt wurde
        if not Datei.X == "X":
            Datei.setStatus("skipped")
            self.onFinished(0, 0)
            return

        # GUI anpassen
        self.pbarpos += self.incr
        self.probar1.setValue(round(self.pbarpos))
        self.btn_start.setEnabled(False)
            
        Datei.setStatus("läuft...")
        self.refreshTable(False)
        self.tbl_files.selectRow(row)
        fname, _ = os.path.splitext(Datei.name)
        self.ts_nach = self.ziel + fname + ".mkv"
        self.ts_von = Datei.fullpath
        self.log.log("\nStart Konvertierung von {0} . . .".format(self.ts_von))
        self.statusbar.showMessage("Umwandlung {0} -> {1}".format(self.ts_von, self.ts_nach))

        # # -----------------------------------------------------------------------------
        # # cmd montieren        
        # self.lastcmd = self.ff.ffXcodeCmd(self.ts_von, self.ts_nach, Datei.video.weite)
        # # self.frameCount = berechneFrameCount(self.ts_von)
        # self.frameCount = Datei.video.frameCount
        # # print("FrameCount:", self.frameCount)     
        # self.log.log("ffmpeg Aufruf: {0}".format(self.lastcmd))
        # # self.log.log("   FrameCount: {0}".format(self.frameCount))
        # self.statusbar.showMessage("Umwandlung {0} -> {1}".format(self.ts_von, self.ts_nach))   

        # if self.frameCount == 0:
        #     self.probar2.setTextVisible(False)
        #     self.probar2.setRange(0,0)  # start hin-her
        #     self.probar2.setValue(0)
        # else:
        #     self.probar2.setTextVisible(True)
        #     self.probar2.setRange(0, self.frameCount)
        #     self.probar2.setFormat("%v")
        #     self.probar2.setValue(0)

        # self.prstart = timer()

        # # Prozess starten
        # self.running = True
        # self.process=QProcess()
        # self.process.finished.connect(self.onFinished)
        # self.process.setProcessChannelMode(QProcess.MergedChannels)
        # self.process.readyReadStandardOutput.connect(self.onReadData)        
        # self.process.start(self.lastcmd)
        # # -----------------------------------------------------------------------------
        self.prstart = timer()
        self.w = transcodeWin.mainApp()
        self.w.wobinich.connect(self.receiver)
        self.w.endeVerarbeitung.connect(self.onFinished)
        self.w.setStartParms(self.ts_von, win=randint(0,3) )
        # self.w.show()


    def progende(self):     # Ende Proc mit Nachfrage
        if self.running:
            reply = QMessageBox.question( self, "Nachfrage",
            "Ablauf abbrechen?\nDas wird nach dem Ende der aktuellen Konvertierung geschehen!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.stopNext = True
                self.statusbar.showMessage("Die Konverierung endet nach dem aktuellen Prozess!")
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
        skipped = 0
        ok = 0
        err = 0
        for ts in self.tsliste.liste:
            if ts.status == "OK":
                ok += 1
            elif ts.status == "warten...  ":                
                wait += 1
            elif ts.status == "skipped":
                skipped += 1
            else:
                err +=1
        if (wait == 0) & (err == 0) & (ok > 0):
            txt = f"\nAlles OK!\n\nOK: {ok}\n" + f"Fehler: {err}\n".format(err) + f"Nicht bearbeitet: {wait + skipped}\n"
            isOK = True
        else:
            txt = f"\nErgebnis!\n\nOK: {ok}\n" + f"Fehler: {err}\n".format(err) + f"Nicht bearbeitet: {wait + skipped}\n"
            isOK = False
        return (txt, isOK)


# def ffmpegBefehl(ts_von, ts_nach):
#         # das "&" stört im Aufruf, es muss maskiert werden
#         von = ts_von.replace("&", "^&")
#         nach = ts_nach.replace("&", "^&")
#         cmd = "c:\\ffmpeg\\bin\\ffmpeg -i "
#         cmd = cmd + "\"{0}\" ".format(ts_von)
#         #cmd = cmd + ' -map 0:v -map 0:a:0 -c:v h264_nvenc -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska '
#         # cmd = cmd + '-c:v h264_nvenc -c:a copy -c:s copy -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska -y '
#         # die folgenden Parameter haben die Eigenschaften (2018-12-13):
#         #  - gute Videoqualität per nvenc;
#         #  - alle Audios werden kopiert
#         #  - Deutscher Untertitel wirde als dvdsub einkopiert
#         #cmd = cmd + '-map 0 -c:v h264_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset fast -f matroska -y '
#         cmd = cmd + '-map 0 -c:v hevc_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset fast -f matroska -y '
        
#         cmd = cmd + "\"{0}\"".format(ts_nach)
#         return cmd


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
    StyleSheet = '''
QProgressBar {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    text-align: center
}
QProgressBar::chunk {
    background-color: #2196F3;
}
#probar1 {
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    text-align: center
}
#probar1::chunk {
    background-color: #2196F3;
}

#probar2 {    
    border: 2px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    text-align: center
}
#probar2::chunk {
    background-color: #2196F3;
}

'''
# color: #2196F3;
#     border: 2px solid #2196F3;
#     border-radius: 5px;


    app = QApplication(sys.argv)  # A new instance of QApplication
    app.setStyleSheet(StyleSheet)
    form = XCodeApp()             # We set the form to be our ExampleApp (design)
    if form.tsliste.size == 0:    # nix zu tun!
        return
    form.show()                   # Show the form
    app.exec_()                   # and execute the app


if __name__ == '__main__':        # if we're running file directly and not importing it
    main()                        # run the main function