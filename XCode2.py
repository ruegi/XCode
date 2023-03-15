# -*- coding: utf-8 -*-
"""
Created on Wed May 16

@author: rg

XCode2.py mit pyqt6
Variante mit start eines separaten Porcesses für den TransCode
angeregt durch start_process.py und ProcessTest.py

Versionen:
1.2     Änderung auf eine ini-Date- die nach SD, HD und FullHD differenziert,
        frame-Zeile in der Statuszeile
1.3     Info Typ als neue Spalte in der Tabelle;
        Fortschrittsbalken in der Spalte 'Status' der Tabelle
2.0     Umbau in eine Hauptprogramm, dass das TrasnCodeWin zum transcodieren x-fach parallel ausführt
2.1     Umstellung auf PyQt6; Einbau des Parameters {canvassize} in ffcmd.ini,
        um den dvdsub-Fehler 'canvas_size(0:0) is too small for render' zu beheben
2.2     neue Farbgebung; Einbau des Parameters {Untertitel} in ffcmd.ini, Fehlerbereinigung
2.3     Entfernung des Tags {Untertitel}; Grund: ffmpeg wertet Tracks, die MeiaInfo als Audiotracks
        ansieht, als Text (also Untertitel) aus. Wenn dann das 'c:v -dvdsub' fehlt, kommt es zu Fehlern.
        Besser ist es, das 'c:v ...' stets mitzugeben.

Offene Probleme:
        - die Farbgebung in den Zellen der Spalte 'Progress' ist zickig, instabil.
        - die Tabelle muss, wenn transcodiert wird, auf readonly gestellt weren; vor allem die 
            Funktion DoppelKlick in der 'X' Spalte.
"""
# from _typeshed import Self
from PyQt6.QtWidgets import (QMainWindow,
                             QTextEdit, 
                             QTableWidget,
                             QWidget,
                             QTableWidgetItem,
                             QHeaderView,
                             QLineEdit, 
                            #  QLabel,
                            #  
                             QPushButton,
                            #  QWidget,
                            #  QHBoxLayout, 
                             QVBoxLayout, 
                             QApplication,
                             QMessageBox,
                             QStyledItemDelegate,
                             QStyleOptionProgressBar,
                             QStyle)

from PyQt6.QtCore import QMutex, QObject, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QTextCursor, QColor, QIcon, QFont, QBrush

from math import log as logarit
from timeit import default_timer as timer
import datetime
import logger
import sys
import time
import os
from random import randint

from pymediainfo import MediaInfo

import liste.liste as liste  # hält eine Liste der umzuwandelnden Dateien

from pymediainfo import MediaInfo

import XCodeUI2 # Hauptfenster; mit pyuic aus der UI-Datei konvertiert

import transcodeWin

tsMutex = QMutex()
anzMutex = QMutex()
logMutex = QMutex()
jobMutex = QMutex()

class Konstanten:                       # Konstanten des Programms
    QUELLE  = "C:\\ts\\"
    ZIEL    = "E:\\Filme\\schnitt\\"
    LOGPATH = "E:\\Filme\\log\\"
    VERSION = "2.3"
    VERSION_DAT = "2023-03-15"
    MAXJOBS = 1     # mehr lohnt nicht!!
    normalFG = QBrush(QColor.fromString("Gray"))
    normalBG = QBrush(QColor.fromString("White"))
    highFG = QBrush(QColor.fromString("White"))
    highBG = QBrush(QColor.fromString("Chocolate"))
    OkFG = QBrush(QColor.fromString("Green"))


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
        self.hoehe = "720"
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
        self.status = status    # "OK", "Fehler", "in Arbeit", "-skip-" oder "warten..."
    
    def toggleXObj(self):
        if self.status == "OK" or self.status == "Fehler" or self.status == "in Arbeit":
            print("keine Änderung")
            return   # keine Änderung, da bereits abgearbeitet

        if self.X == "X":
            self.X = ""
            self.status = "-skip-"
        else:
            self.X = "X"
            self.status = "warten..."
        return
  

class jobControl():
    '''
    Diese Klasse beschreibt einen Tanscoder Job.
    alle Meldungen werden in einen Klassen-Lokalen Buffer geschrieben und bei JobEnde
    in die Logdatei transferiert    
    '''
    def __init__(self, index, tsObj):
        self.index = index
        self.tsObj = tsObj
        self.thread = None
        self.window = None
        self.worker = None
        self.start_time  = 0
        self.end_time = 0
        self.logBuffer = ""


class ladeFenster(QWidget):
    '''
    ein Fenster, das den Ladevorgang zeigt
    '''
    def __init__(self, callerWin):
        super().__init__()        
        self.callerWin = callerWin
        self.resize(800, 80)
        self.setStyleSheet("ladeFenster {background-color: #fff5cc;}")
        self.setWindowTitle("XCode2: Filme laden . . .")
        self.setWindowIcon(QIcon("XC.ico"))
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.zeile = QLineEdit("XCode2: Filme laden . . .")
        self.zeile.setReadOnly(True)
        self.zeile.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.zeile.setFont(QFont('Arial', 12))
        layout.addWidget(self.zeile)
        self.btn_abbruch  = QPushButton("Abbruch", self)
        self.btn_abbruch.clicked.connect(self.abbruchApp)
        layout.addWidget(self.btn_abbruch)

    def abbruchApp(self):
        self.callerWin.processkilled = True

    def setZeile(self, txt):
        self.zeile.setText(txt)
        QApplication.processEvents()


class ProgressDelegate(QStyledItemDelegate):
    '''
    Mit der paint-Methode des Delegates können die Progress-Bars in der letzten Spalte konfiguriert werden
    Dabei taucht ein Problem auf:
    dieses Objekt hat keine Verbindung zu den anderen Objekten zur Laufzeit.
    Um den den aktuellen Fortschritt zu erhalten, muss dieser in diesem Zell-Item als User-Data hinterlegt werden.
    Das geschieht mit "index.data(Qt.ItemDataRole.UserRole+1000)" (beim lesen) und 
    "setData(index.data(Qt.ItemDataRole.UserRole+1000), prozent)" beim schreiben.
    Noch kenne ich keinen Weg, die häßliche grüne Farbe des Chunk zu ändern ...
    rg, 2021-07-25
    '''
    def paint(self, painter, option, index):
        smallBarStyle = """
        QProgressBar{
    border: 2px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: Chocolate;
}
        """
        progress = index.data(Qt.ItemDataRole.UserRole+1000)
        if progress is None: progress = 0
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect        
        opt.textAlignment = Qt.AlignmentFlag.AlignCenter
        opt.minimum = 0
        opt.maximum = 100  
        opt.setStyleSheet(smallBarStyle)
        opt.progress = progress
        opt.text = f"{progress}%"
        opt.textVisible = True
        opt.state |= QStyle.StateFlag.State_Horizontal
        QApplication.style().drawControl(QStyle.ControlElement.CE_ProgressBar, opt, painter)
        #    QStyle.CE_ProgressBar, opt, painter)        


class XCodeApp(QMainWindow, XCodeUI2.Ui_MainWindow):

    def __init__(self):               
        super(self.__class__, self).__init__()
        
        self.setupUi(self)  # This is defined in XCodeUI.py file automatically
                            # It sets up layout and widgets that are defined

#         pbarsheet = '''
# QProgressBar {
#     border: 2px solid #2196F3;
#     border-radius: 5px;
#     background-color: #E0E0E0;
#     text-align: center
# }
# QProgressBar::chunk {
#     background-color: #2196F3;
# }'''        

        # Instanz-Variablen
        self.frameCount = 0
        self.process = None
        self.processkilled = False
        self.quelle  = Konstanten.QUELLE
        self.ziel    = Konstanten.ZIEL
        self.logpath = Konstanten.LOGPATH
        self.tsliste = liste.liste()  # Liste der ts-Objekte
        self.running = 0        # ANzahl laufender Transcode-Prozesse
        self.stopNext = False   # HalteSignal
        self.incr = 0.0         # Increment des Procbar1
        self.pbarpos = 0        # Pos des ProcBar1
        self.prstart = 0        # start timer des prozesses
        self.prend = 0          # end timer
        self.ts_von = ""        # aktuelle quelle
        self.ts_nach = ""       # aktuelles ziel
        self.lastcmd = ""       # letzter cmd, der im Prozess verarbeitet wurde
        self.jobList = []       # Liste der laufenden Jobs als JobControl Objekte
        self.app = QApplication.instance()
        for i in range(0, Konstanten.MAXJOBS):
            self.jobList.append(None)

        # Icon versorgen
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + 'XC.ico'))

        # Feintuning der Widgets
        self.tbl_files.setHorizontalHeaderLabels(("Nr", 'X', 'Datei', 'Typ', 'Progress', 'Status'))
        self.tbl_files.setAlternatingRowColors(True)
        # delegate = ProgressDelegate(self.tbl_files)
        # self.tbl_files.setItemDelegateForColumn(4, delegate)

        header = self.tbl_files.horizontalHeader()  
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        # header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.tbl_files.setAlternatingRowColors(True)

        self.lbl_version.setText( "XCode Version " + Konstanten.VERSION + " vom " + Konstanten.VERSION_DAT )
        
        cName = "darkCyan"
        
        self.le_pfad.setDisabled(True)
        self.probar1.setValue(0)
        self.probar2.setValue(0)
                
        # connects
        self.btn_ende.clicked.connect(self.progende)
        self.btn_start.clicked.connect(self.convert)
        self.tbl_files.doubleClicked.connect(self.toggleX)
        
        # Abschluss Init; laden der Daten
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log = logger.logFile(self.logpath + "XCode_"+ self.dt + ".log", TimeStamp=True, printout=False)

        self.setWinPos()        
        self.ladeFiles(self.quelle)

        if self.tsliste.size == 0:
            reply = QMessageBox.information( self, "Hinweis",
            f"Es gibt im Ordner {self.quelle} keine ts-Dateien.\nNichts zu tun!")
            return
        else:
            self.incr = 100.0 / self.tsliste.size
        self.statusbar.showMessage("{0} Dateien geladen!".format(self.tsliste.size))

    def setWinPos(self):
        screen = self.app.primaryScreen()
        w = screen.availableGeometry().width()
        h = screen.availableGeometry().height()        
        x = 10
        y = 10
        self.move(x,y)

    
    def toggleX(self):
        # zunächst die aktuelle Zeile finden        
        idx = self.tbl_files.selectedIndexes()[0]
        row = idx.row()        
        Datei = self.tsliste.getRow(row)
        if Datei is None:
            return
        else:
            Datei.toggleXObj()
            self.refreshTableRow(row)    # kein Neuaufbau
            self.tbl_files.selectRow(row)
        return         


    def setRowProgress(self, row, zahl):
        zahl = 100 if zahl > 100 else zahl
        anzMutex.lock()        
        itm = self.tbl_files.item(row, 4)
        itm.setText(str(zahl) + " %")
        self.probar2.setValue(zahl)
        # itm.setData(Qt.ItemDataRole.UserRole+1000, zahl) 
        anzMutex.unlock()


    def receiver(self, index, zahl):
        # empfängt die Fortschrittszahlen des Subwindow
        # und zeigt den Fortschritt im Zeilen-Fortschritts-Balken an
        
        # print("Receiver: Index: ", index, "Zahl: ", zahl)
        row = self.jobList[index].tsObj.nr
        self.jobList[index].tsObj.progress = zahl
        self.setRowProgress(row, zahl)
        

    # Funktionen
    def ladeFiles(self, ts_pfad):     # lädt die ts-Files
        # stopReq = False
        # def stopAnforderung():
        #     global stopReq
        #     stopReq = True

        ladeWin = ladeFenster(self)
        ladeWin.show()
        # Liste der ts-files laden
        i = 0
        for entry in os.scandir(ts_pfad):
            if self.processkilled:
                break
            if entry.is_file():
                fname, fext = os.path.splitext(entry.name)
                if fext in [".ts", ".mpg", ".mp4", ".mkv", ".mv4", ".mpeg", ".avi"]:
                    i += 1
                    fullpath = os.path.join(ts_pfad, entry.name)
                    ladeWin.setZeile(f"({i}) - {fullpath}")
                    tse = tsEintrag(i-1, fullpath, entry.name, fext, "warten...")
                    self.tsliste.append(tse)
                    self.log.log("Lade: {0:2}: {1}".format(i, entry.name))
        self.tsliste.findFirst()
        ladeWin.close()
        
        if self.processkilled:            
            self.close()
            self.app.quit()

        self.refreshTable(True)        
        return self.tsliste.size


    def refreshTable(self, neuaufbau):
        # das Table-widget füllen
        if neuaufbau:
            self.tbl_files.setRowCount(0)
        for ts in self.tsliste.liste:
            # print(ts)
            # direkte Benutzung der tsliste, ohne die Werte von lastPos und lastObj zu verändern
            nr = ts.nr
            if neuaufbau:
                self.tbl_files.insertRow(nr)
                self.tbl_files.setItem(nr, 0, QTableWidgetItem(str(ts.nr)))
                self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.X))
                self.tbl_files.setItem(nr, 2, QTableWidgetItem(ts.name))
                self.tbl_files.setItem(nr, 3, QTableWidgetItem(ts.video.typ))
                self.tbl_files.setItem(nr, 4, QTableWidgetItem(" "))

                # zentrieren
                self.refreshTableRow(nr)
                itm = self.tbl_files.item(nr, 0)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # itm = self.tbl_files.item(nr, 1)
                # itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                itm = self.tbl_files.item(nr, 3)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # itm = self.tbl_files.item(nr, 5)
                # itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                if nr == self.tsliste.lastPos:
                    self.refreshTableRow(nr)
                    break

        self.tbl_files.selectRow(self.tsliste.lastPos)

    def refreshTableRow(self, row):
        # aktualisiert nur eine einzelne Zeile
        # in den Spalten 1, 4, 5
        # muss dafür das passende tsObj finden
        tsObj = self.tsliste.liste[row]
        self.tbl_files.setItem(row, 1, QTableWidgetItem(tsObj.X))
        itm = self.tbl_files.item(row, 1)
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        itm = self.tbl_files.item(row, 4)
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if tsObj.status == "in Arbeit...":
            itm.setText(str(tsObj.progress) + " %")
            itm.setBackground(Konstanten.highBG)
            itm.setForeground(Konstanten.highFG)            
        elif tsObj.status == "OK":
            itm.setText("erledigt")
            itm.setBackground(Konstanten.OkFG)
        elif tsObj.status == "warten...":
            itm.setText("--->")
            itm.setBackground(Konstanten.normalBG)
            itm.setForeground(Konstanten.normalFG)
        else:            
            itm.setText("-?->")
            itm.setBackground(Konstanten.normalBG)
            itm.setForeground(Konstanten.normalFG)
        
        self.tbl_files.setItem(row, 5, QTableWidgetItem(tsObj.status))
        itm = self.tbl_files.item(row, 5)
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl_files.selectRow(row)


    def run_a_single_job(self, index)->jobControl:
        '''
        startet eine einzelnen Job;
        gibt bei Fehler oder wenn nichts mehr zu tun ist 'None' zurück
        '''
        if self.stopNext:   # Abbruch angefordert, kein neuer Start
            # print("nix wg stopNext")
            return None
        
        tsObj = self.findeArbeit()      # setze status auf "in Arbeit"
        if tsObj is None:       # nichts (mehr) zu tun
            # print("nix wg None")
            return None
        self.statusbar.showMessage("transcoding . . . " + tsObj.name)
        self.probar2.setRange(0,100)     
        self.probar2.setFormat("%p %")
        self.probar2.setTextVisible(True)
        self.probar2.setValue(0)
        myJob = jobControl(index, tsObj)
        myJob.start_time = timer()
        myJob.window = transcodeWin.mainApp(myJob.tsObj.fullpath, myJob.index) 
        myJob.window.wobinich.connect(lambda zahl: self.receiver(myJob.index, zahl))
        myJob.window.JobEnde.connect(self.endWinProc)
        myJob.start_time = timer()
        myJob.window.show()
        self.setFocus()
        self.tbl_files.setFocus()

        # Farbgebung für den Fortschrittsbalken der aktiven Zeile
        itm = self.tbl_files.item(tsObj.nr, 4)
        itm.setBackground(Konstanten.highFG)
        itm.setForeground(Konstanten.highBG)
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pbarpos += self.incr
        self.probar1.setValue(round(self.pbarpos))
        self.refreshTableRow(tsObj.nr)
        self.logJob(f"Start Konvertierung in {myJob.index} von {myJob.tsObj.fullpath}")
        return myJob


    def findeArbeit(self) -> tsEintrag:
        ''' Sucht in der tsListe nach einem noch freien Eintrag und gibt ihn als tsObj zurück.
            Wird nichts gefunden, wird None zurückgegeben
            Besonderheit hier: es ist für konkurrenten Zugriff abgesichert.
        '''
        Obj = None
        tsMutex.lock()
        for tsObj in self.tsliste.liste:            
            if tsObj.X == "X" and tsObj.status == "warten...":
                # print("Gefunden: ", tsObj)
                tsObj.status = "in Arbeit..."
                Obj = tsObj
                self.refreshTableRow(tsObj.nr)
                break 
        tsMutex.unlock()        
        return Obj


    def endWinProc(self, index, exitCode, exitStatus):
        # print("In XCode:endWinProc")
        myJob = self.jobList[index]
        myJob.end_time = timer()
        myJob.is_running = False
        # print("In XCode2.py endWinProc")
        myJob.logBuffer += f"\nExitCodes: ExitCode={exitCode}, ExitStatus={exitStatus}"
        # print(f"ExitCodes: ExitCode={exitCode}, ExitStatus={exitStatus}")
        m, s = divmod(myJob.end_time - myJob.start_time, 60)
        h, m = divmod(m, 60)
        time_str = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h, m, s)        
        myJob.logBuffer += f"\nDauer: {time_str}"
        # print('Stopping thread...',self.index)        
        myJob.window.close()
        myJob.window = None
        if exitCode > 0:
            self.processkilled = True
        self.jobEnde(myJob, exitCode)


    def convert(self):
        '''
        konvertiert eine ts-Datei über einen separaten Prozess
        '''
        self.btn_start.setEnabled(False)
        for index in range(0, Konstanten.MAXJOBS):
            myJob = self.run_a_single_job(index)
            self.jobList[index] = myJob
            if myJob is None:       # vorzeitiges Ende
                break
     

    def logJob(self, logTxt: str):
        logMutex.lock()
        self.log.log(logTxt)
        logMutex.unlock()


    def jobEnde(self, job: jobControl, exitCode: int):
        # das Ergebnis des Jobs wegschreiben und ggf. neuen Job aufmachen
        index = job.index
        l = "Ende Job [" + job.tsObj.fullpath + "]\n"        
        if exitCode > 0:
            pro = 0
            job.tsObj.status = "Fehler"
        else:
            pro = 100
            job.tsObj.status = "OK"        
        job.tsObj.progress = pro        
        self.probar2.setValue(0)
        # den Farbcode des Fortschritts-Feldes in der Tabelle zurücksetzen
        itm = self.tbl_files.item(job.tsObj.nr, 4)
        itm.setBackground(Konstanten.normalFG)
        itm.setForeground(Konstanten.normalBG)
        itm.setText("--->")

        if self.running > 0:
            self.running -= 1

        self.setRowProgress(job.tsObj.nr, pro)
        self.refreshTableRow( job.tsObj.nr)
        self.logJob(l + job.logBuffer)
        
        time.sleep(0.1)    # sleep 100 ms for housekeeping

        if self.processkilled or exitCode > 0:
            return
        
        job = self.run_a_single_job(index)
        self.jobList[index] = job       # egal, ob None oder echter Job
        if job is None:
            if self.running == 0:
                self.statusbar.showMessage("Ende der Verarbeitung!")
                self.ende_verarbeitung()
            return
        else:
            # das running Flag korrekt setzen
            jobMutex.lock() 
            self.running += 1
            # self.running = False
            # for i in range(0, Konstanten.MAXJOBS):
            #     if not self.jobList[i] is None:
            #         self.running = True
            #         break
            jobMutex.unlock()
        return


    def progende(self):     # Ende Proc mit Nachfrage
        # print("self.running = ", self.running)
        if self.running > 0:
            reply = QMessageBox.question( self, "Nachfrage",
            "Ablauf abbrechen?\nDas wird nach dem Ende der aktuellen Konvertierung geschehen!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.stopNext = True
                self.statusbar.showMessage("Die Konverierung endet nach den aktuellen Prozessen!")
                self.btn_ende.setText("Abbruch angefordert!")
                self.btn_ende.setDisabled(True)
            else:
                return
        else:
            self.ende_verarbeitung()
        
    def ende_verarbeitung(self):
        self.tbl_files.selectRow(-1)
        self.log.log("-" * 80)        
        self.statusbar.showMessage("Verarbeitung beendet!")
        if self.btn_start.isEnabled():
            self.log.log("Nichts getan!")
        else:
            if self.stopNext:
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
            elif ts.status == "warten...":                
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

    # probar1 bg-color #2196F3;;

    StyleSheet = '''
QMainWindow {
    background-color: #fff5cc;
}
QTableWidgt {
    background-color: DimGray;
}

QPushButton {
        color: white;
        background-color: Chocolate;
        border-style: outset;
        border-width: 1px;
        border-radius: 5px;
        border-color: black;        
        padding: 3px;
    }

QProgressBar {
    color: White;
    border: 1px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    text-align: center
}
QProgressBar::chunk {
    background-color: Chocolate;
}

#probar1 {
    color: White;
    border: 1px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    border-color: Black;
    text-align: center
}
#probar1::chunk {
    background-color: Chocolate;
}

#probar2 {
    color: Black;
    border: 1px solid #2196F3;
    border-radius: 5px;
    background-color: #E0E0E0;
    border-color: Black;
    text-align: center
}
#probar2::chunk {
    background-color: Chocolate;
}


'''
# color: #2196F3;
#     border: 2px solid #2196F3;
#     border-radius: 5px;
# #probar2 {    
#     border: 2px solid #2196F3;
#     border-radius: 5px;
#     background-color: #E0E0E0;
#     text-align: center
# }
# #probar2::chunk {
#     background-color: #2196F3;
# }



    app = QApplication(sys.argv)  # A new instance of QApplication
    app.setStyleSheet(StyleSheet)
    form = XCodeApp()             # We set the form to be our ExampleApp (design)
    if form.tsliste.size == 0:    # nix zu tun!
        return
    form.show()                   # Show the form
    if not form.processkilled:
        app.exec()                   # and execute the app


if __name__ == '__main__':        # if we're running file directly and not importing it
    main()                        # run the main function
