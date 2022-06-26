# -*- coding: utf-8 -*-
"""
Created on 2021-07-27

@author: rg

Hauptprogramm mit pyqt5

Dieses Window transcodiert ein Video in ein HEVC-MKV mit Hilfe von ffmpeg und einer ffcmd.ini

"""
from PyQt5.QtWidgets import (QMainWindow, 
#                             QLabel, 
#                             QLineEdit, 
#                             QPushButton,
#                             QWidget,
                             QApplication, 
                             QFileDialog,
                             QMessageBox,
                             QDesktopWidget
                             )

from PyQt5.QtGui import QIcon, QTextCursor          #, QColor,
from PyQt5.QtCore import Qt, QProcess, pyqtSignal   # , QObject, 

import sys
import os
import shutil
from pathlib import Path
from math import log as logarit
from random import randint

from pymediainfo import MediaInfo
from datetime import timedelta, datetime
from timeit import default_timer as timer

import videoFile
import configparser
import logger
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
    INIDATEI = r'.\ffcmd.ini'
    XCODEZIEL = 'E:\\Filme\\schnitt\\'
    LOGPATH = 'E:\\Filme\\log\\'
    MUSTER_FFMCMD = '''\    
[SD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset fast -profile:v main10 -pix_fmt p010le -crf 28 -b:v 0 -maxrate 2M -bufsize 4M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"

[HD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 3M -bufsize 6M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"

[FullHD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 4M -bufsize 8M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"
'''

class mainApp(QMainWindow, transcodeWinUI.Ui_MainWindow):
    # Signal to calling window        
    wobinich = pyqtSignal(int, name="wobinich")
    JobEnde = pyqtSignal(int, int, int)

    def __init__(self, file=None, win=0):               
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in ...UI.py file automatically
                            # It sets up layout and widgets that are defined

        # Instanz-Variablen
        self.video = None
        self.cmd = ""
        self.process = None
        self.processkilled = False
        self.running = False
        self.prstart = 0        # start timer des prozesses
        self.prend = 0          # end timer
        self.ts_von = ""
        self.ts_nach  = ""
        self.stopnext = False
        dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log = None
        self.nr = win     # randint(0,3)
        # self.progressSignal = pyqtSignal(int, name="progressSignal")
        self.app = QApplication.instance()
        # print("IN transcodeWin", file, win)
        if not file is None:
            self.setWinPos()
            self.le_quelle.setText(file)
        
        # Icon versorgen
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QIcon(scriptDir + os.path.sep + Konstanten.ICON))

        # # Feintuning der Widgets
        self.te_ffmpeg.setReadOnly(True)
        # self.cbGruppen.addItem("ohne")
        self.progressBar.setRange(0,100)
        self.progressBar.setValue(0)

        self.btn_start.setEnabled(True)

        # connects
        self.btn_stop.clicked.connect(self.progende)
        self.btn_quelle.clicked.connect(self.openFileNameDialog)
        # self.leName.installEventFilter(self)  # Eventfilter wie FocusIn und Out montieren
        # self.btn_start.
        self.btn_start.clicked.connect(self.startButProg)
        self.btn_stop.setFocus()

        # print("IN transcodeWin 2")
       
        if self.le_quelle.text() is None or self.le_quelle.text() == "":
            # Fensterposition
            self.setWinPos()
            # print("IN transcodeWin 2a")            
        else:
            # print("IN transcodeWin 2b")
            self.startButProg()
            # self.startjob()
        # if self.video is None:
        #     self.show()               # Show the form
    
    def setWinPos(self):
        screen = self.app.primaryScreen()
        # alte Logik
        # w = screen.availableGeometry().width() / 2
        # h = screen.availableGeometry().height() / 2
        # m = self.nr % 4
        # y = int(h*(self.nr % 2))
        # x = int(w*(m // 2))

        # neue Logik
        w = screen.availableGeometry().width()
        h = screen.availableGeometry().height()
        m = (self.nr+1) % 4     # m = 0 .. 3; start bei 1
        if m % 2 == 1:  # 1 oder 3
            # x = int(w/2)
            x = w - self.geometry().width()
        else:
            x = 0
        if m > 1:   # 2 oder 3
            # y = int(h/2)
            y = h - self.geometry().height() - 40
        else:
            y = 0
        self.move(x,y)

    def startButProg(self):
        vn = self.le_quelle.text()
        if os.path.isfile(vn):
                self.video = videoFile.videoFile(vn)                
            
        if self.video is None:
            self.statusbar.showMessage(f"Video '{vn}' nicht gefunden!")
        else:
            dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.log = logger.logFile(Konstanten.LOGPATH + "TransCode_(" + dt + ") (" + self.video.name + ").log", TimeStamp=True, printout=False)
            self.btn_quelle.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_stop.setFocus()
            self.ts_von = vn
            self.ts_nach = Konstanten.XCODEZIEL + self.video.name + ".mkv"
            self.prepVideoX(self.video)
            self.statusbar.showMessage("OK!")
            # print("IN transcodeWin - Vor startjob")

            self.startjob()
        return

    def prepVideoX(self, vidObj):
        '''
        - ini-Datei auswerten,
        - passende cmd aufbauen
        - message slot verdrahten
        - cmd starten
        '''
        self.getCmd()
        durstr = str(timedelta(seconds=self.video.duration/1000))
        anz = f"Film: {self.ts_von}\n"
        anz += f"Auflösung: {self.video.weite}x{self.video.hoehe} ({self.video.typ})\n"
        anz += f"Dauer: {self.video.duration} ms (={durstr}) ({self.video.frameCount} Frames)\n"
        anz += "\nffmpeg-Aufruf:\n" + "-"*80 + "\n" + self.cmd + "\n" + "-"*80 + "\n"
        self.te_ffmpeg.setPlainText(anz)
        self.log.log(anz)

    def onReadProcessData(self):
        txt = self.process.readAllStandardOutput().data().decode('cp850')
        if txt.startswith("frame="):
            self.le_frames.setText("> " + txt)
            data = txt.split("=")   # frame=344874 fps=136 q=20.0 Lsize= 3003827kB time=01:54:59.46 bitrate=3566.6kbits/s speed=2.72x
            txtAnzFr = data[1].strip().split(" ")            
            try:
                anzFrames = int(txtAnzFr[0])
            except:
                anzFrames = 0
            pro = 0
            if self.video.frameCount > 0:
                if anzFrames > self.video.frameCount:
                    anzFrames = self.video.frameCount
                pro = int(anzFrames/self.video.frameCount*100)
                self.progressBar.setValue(pro)  # Anzeige der Position
                self.wobinich.emit(pro)
            # print("txtAnzFr: ", txtAnzFr, " ,Frame:", anzFrames," von ", self.video.frameCount, "Prozent:", pro)
        else:            
            self.te_ffmpeg.appendPlainText(txt)
            self.te_ffmpeg.moveCursor(QTextCursor.End)
            self.log.log(txt)
        
    def closeProcessEvent(self, event):
        # print("In closeProcessEvent")
        if self.running:
            reply = QMessageBox.warning(self, "Achtung!",
                                            "Laufende Konvertierung abbrechen?\nDas macht das neu erzeugte Video unbrauchbar!",
                                            QMessageBox.Yes | QMessageBox.No,
                                            QMessageBox.No)
            if reply == QMessageBox.No:
                self.processkilled = False
                event.ignore()  # hier kein weiterer close (wegen self.running)!
        else:
            self.processkilled = True
            self.ende_verarbeitung()
            event.accept()


    def onFinished(self, exitCode, exitStatus):
        # print("IN TranscodeWin:onFinished")
        self.prend = timer()
        self.running = False        
        m, s = divmod(self.prend - self.prstart, 60)
        h, m = divmod(m, 60)
        time_str = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h, m, s)        
        if exitStatus == 0:
            if exitCode == 0:   # Abschluss-Verarbeitung, wenn alles gut gelaufen ist
                self.log.log(self.le_frames.text() )
                qlen = os.stat(self.ts_von).st_size
                try:
                    zlen = os.stat(self.ts_nach).st_size
                except:
                    zlen = 0    
                self.log.log("{0} --> {1} ({2:2.2f}%)".format(format_size(qlen), format_size(zlen), zlen / qlen * 100))
                self.log.log(f"Dauer: {time_str}; ReturnCode: {exitCode}")
                self.log.log("OK")
                try:
                    shutil.move(self.ts_von, self.ts_von + ".done")
                except:
                    self.log.log("Warnung: Konnte die QuelleDatei nicht in *.done umbenennen!")
                                
            else:       # Abschluss-Verarbeitung bei Fehler
                self.log.log("Fehler! ReturnCode: {0}".format(exitCode))
                self.log.log("Letzter Befehl:\n{0}".format(self.cmd))                
        else:            
            if self.processkilled:
                self.log.log("Harter Abbruch! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))                
            else:
                self.log.log("Fehler! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
        
        self.JobEnde.emit(self.nr, exitCode,  exitStatus)
        if not self.processkilled: 
            self.ende_verarbeitung()        
        return 

    def getCmd(self):
        '''
        liest die IniDatei ein und gibt den passenden cmd zurück
        liest dafür das video-Objekt aus
        '''
        pFile = Path(Konstanten.INIDATEI)
        if not pFile.is_file():
            # sofort eine default-Ini-Datei mit default Eintrag erzeugen            
            cmd = Konstanten.MUSTER_FFMCMD
            with open(self.initFile, "w") as iniFHdl:
                iniFHdl.write(cmd)

        # die aktuellen ffmpeg-Aufrufe merken
        config = configparser.ConfigParser()   
        config.read(Konstanten.INIDATEI)
        if self.video.typ == "SD":
            self.cmd = config.get('SD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset fast -profile:v main10 -pix_fmt p010le -crf 28 -b:v 0 -maxrate 2M -bufsize 4M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')            
        elif self.video.typ == "HD":
            self.cmd =  config.get('HD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 3M -bufsize 6M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')
        else:
            self.cmd = config.get('FullHD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 4M -bufsize 8M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')

        if self.cmd.index("{EingabeDatei}") > -1:
            self.cmd = self.cmd.replace("{EingabeDatei}", self.video.fullPathName)        
        if self.cmd.index("{AusgabeDatei}") > -1:
            ausgabe = Konstanten.XCODEZIEL + self.video.name + ".mkv"
            self.cmd = self.cmd.replace("{AusgabeDatei}", ausgabe)


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
        self.prstart = timer()
        # Prozess starten
        self.running = True
        self.process=QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.onReadProcessData)        
        self.process.start(self.cmd)
        # print("In startjob Nach Process Start")


    def ende_verarbeitung(self):
        ''' Abschlussarbeiten '''
        # print("In ende_verarbeitung")
        self.statusbar.showMessage("Verarbeitung beendet!")
        if self.btn_start.isEnabled():
            if not self.log is None: self.log.log("Nichts getan!")
        else:
            if self.processkilled:                
                # self.process.kill()
                self.process.terminate()
                t = 0
                while self.running:
                    t += 1
                    self.Hinweis(f"{t}: Warte auf das Ende von ffmpeg...")
                    QApplication.processEvents()
                    self.process.waitForFinished(1000)
                    if t > 5:
                        self.process.kill()
                    elif t > 10:
                        break
                    else:
                        pass

                if os.path.isfile(self.ts_nach):    #die defekte Datei löschen
                    try:  # versuchen, die kaputte *.mkv"-datei zu löschen
                        os.remove(self.ts_nach)
                    except:
                        QMessageBox.information(self, "Achtung!",
                                                "Die defekte Datei \n{0}\nkonnte NICHT gelöscht werden!".format(
                                                    self.ts_nach))
                        if not self.log is None: self.log.log("Defekte Zieldatei [{0}] konnte NICHT gelöscht werden!")
                    else:
                        if not self.log is None: self.log.log("Defekte Zieldatei wurde gelöscht!")
                # if not self.log is None: self.log.log("Harter Abbruch!")
                # txt = "Harter Abbruch!"
                # if not self.log is None: self.log.log("Ende nach Abbruch!" )
            else:
                # print("nicht in killed!")
                txt = "Programm-Ende!"
                if not self.log is None: self.log.log("Ende!")
        if not self.log is None: self.log.close()
        self.running = False
        self.close()
        
    
    def setStartParms(self, datei, win=0):
        # print("IN transcodeWin.setStartPos")
        self.le_quelle.setText(datei)
        self.nr = win
        self.startButProg()
        self.setWinPos()
        self.show()
                
    # Funktionen
    def progende(self):     # Ende Proc mit Nachfrage
        reply = QMessageBox.question( self, "Nachfrage",
            "Ablauf abbrechen?\nDie aktuelle Konvertierung wird beendet und das halbfertige Ergebnis wird gelöscht werden!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.processkilled = True
            # print("IN progende")
            self.ende_verarbeitung()
        else:
            return

   
    def Hinweis(self, nachricht ):        
        self.statusbar.showMessage(nachricht)        


    def openFileNameDialog(self)->str:
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        # fileName, _ = QFileDialog.getOpenFileName(self, "ein Video aussuchen", os.getcwd(),"Videos (*.ts);;All Files (*)", options=options)
        fileName, _ = QFileDialog.getOpenFileName(self, "einen Film aussuchen", "E:\\Filme\\", "All Files (*);;Filme (*.mkv *.mpg *.mp4 *.ts *.avi)", options=options)
        if fileName:
            self.le_quelle.setText(fileName)
            return fileName
        else:
            return None


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

        
def main(pname, win):
    # global pname
    app = QApplication(sys.argv)  # A new instance of QApplication
    form = mainApp(file=pname, win=win)              # We set the form to be our App (design)    
    # if not pname is None and pname > "": 
    #     form.setStartParms(pname, win=win)
        # print(f"{form.le_quelle.text()} gesetzt!")
    form.show()
    app.exec()                   # and execute the app
    return form
    


if __name__ == '__main__':        # if we're running file directly and not importing it
    pname = None
    win = 0
    if len(sys.argv) > 1:
        pname = sys.argv[1].strip()
        if len(sys.argv) > 2:
            win = int(sys.argv[2].strip())
    
    main(pname, win)                        # run the main function
    