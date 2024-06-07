# -*- coding: utf-8 -*-
#
# Created on Wed May 16

# @author: rg

# XCode.py mit pyqt
# Variante mit start eines separaten Porcesses für den TransCode
# angeregt durch start_process.py und ProcessTest.py

# Versionen:
# 1.2     Änderung auf eine ini-Datei- die nach SD, HD und FullHD differenziert,
#         frame-Zeile in der Statuszeile
# 1.3     Info Typ als neue Spalte in der Tabelle;
#         Fortschrittsbalken in der Spalte 'Status' der Tabelle
# 2.0     Umstellung auf PyQt6; erweiterter Parameter -canvas_size ... in ffmpeg,
#         um den dvdsub-Fehler 'canvas_size(0:0) is too small for render' zu beheben
# 2.1-2.2 siehe XCode2
# 2.3     Aufgehübscht, videoFile.py und ffcmd.py eingebaut, frame-Zeile separat
# 2.4     Probleme in der Anzeige, die nach Umstellung auf AV1 enstanden sind, wurden behoben
# 2.5     Weiterarbeit an den Anzeigeproblemen; kompatibilität der Ausgaben von hevc und av1 Encodern hergestellt
# 2.51    progress-Logging abgeschaltet und nach c:\temp verschoben
# 2.6     Bessere Darstellung um edit-Widget
# 2.7     Darstellung für ffmpeg hvenc & ffmpeg AV1 stimmig
# 2.8     automatischer Rückfall in den Nur-Copy-Modus, wenn das Ziel größer als die Quelle geworden ist.
#         Dafür gibt es ab jetzt den Abschnitt [Copy] in der ffcmd.ini
# 2.9     Erweiterung des Ergebnisses um Summen der Original- und der Codierten Länge
# 2.10    Erweiterung der Qualitäts-Anzeige (per reg-Ausdrücke) in Split-Parms
# 2.11    Umstellung von pyinstaller auf nuitka Compile; size= wird jetzt mit Tausender-Punkten formatiert
#
#
from PyQt6.QtWidgets import (
    QMainWindow,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStyle,
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
    QStyle,
)

from PyQt6.QtCore import QProcess, QObject, Qt
from PyQt6.QtGui import QTextCursor, QFont, QIcon, QColor, QBrush

from math import log as logarit
from timeit import default_timer as timer
import datetime
import logger
import sys
import shutil
import os
from random import randint
import re

import liste.liste as liste  # hält eine Liste der umzuwandelnden Dateien

import videoFile
import ffcmd
import XCodeUI  # Hauptfenster; mit pyuic aus der UI-Datei konvertiert


class Konstanten:  # Konstanten des Programms
    QUELLE = "C:\\ts\\"
    ZIEL = "E:\\Filme\\schnitt\\"
    LOGPATH = "E:\\Filme\\log\\"
    VERSION = "2.11"
    VERSION_DAT = "2024-05-29"
    normalFG = QBrush(QColor.fromString("Gray"))
    normalBG = QBrush(QColor.fromString("White"))
    highFG = QBrush(QColor.fromString("White"))
    highBG = QBrush(QColor.fromString("Chocolate"))
    OkFG = QBrush(QColor.fromString("Green"))
    iconFile = "D:\\Dev\\Py\\XCode\\XC_1.ico"
    logProgress = False  # 4 debug
    ffmpegLog = r"C:\temp\ffmpegLog"


class ladeFenster(QWidget):
    """
    ein Fenster, das den Ladevorgang zeigt
    """

    def __init__(self, callerWin):
        super().__init__()
        self.callerWin = callerWin
        self.resize(800, 80)
        self.setStyleSheet("ladeFenster {background-color: #fff5cc;}")
        self.setWindowTitle("XCode: Filme laden . . .")
        # self.setWindowIcon(QIcon(Konstanten.iconFile))
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.zeile = QLineEdit("XCode: Filme laden . . .")
        self.zeile.setReadOnly(True)
        self.zeile.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.zeile.setFont(QFont("Arial", 12))
        layout.addWidget(self.zeile)
        self.btn_abbruch = QPushButton("Abbruch", self)
        self.btn_abbruch.clicked.connect(self.abbruchApp)
        layout.addWidget(self.btn_abbruch)

    def abbruchApp(self):
        self.callerWin.processkilled = True

    def setZeile(self, txt):
        self.zeile.setText(txt)
        QApplication.processEvents()


class tsEintrag:
    def __init__(self, nr, fullpath, name, ext, status):
        self.nr = nr
        self.X = "X"
        self.fullpath = fullpath
        self.name = name
        self.status = status
        self.progress = 0
        self.copyMode = False
        self.video = videoFile.videoFile(fullpath)
        self.org_len = 0
        self.xcode_len = 0

    def __str__(self):
        return "{0}: {1} mit Status {2}".format(self.nr, self.fullpath, self.status)

    def setStatus(self, status):
        self.status = status

    def toggleXObj(self):
        if self.status == "OK" or self.status == "Fehler" or self.status == "in Arbeit":
            # print("keine Änderung")
            return  # keine Änderung, da bereits abgearbeitet

        if self.X == "X":
            self.X = ""
            self.status = "-skip-"
        else:
            self.X = "X"
            self.status = "warten..."
        return


class ProgressDelegate(QStyledItemDelegate):
    """
    Mit der paint-Methode des Delegates können die Progress-Bars in der letzten Spalte konfiguriert werden
    Dabei taucht ein Problem auf:
    dieses Objekt hat keine Verbindung zu den anderen Objekten zu Laufzeit.
    Um den aktuellen Fortschritt zu erhalten, muss dieser in diesem Zell-Item als User-Data hinterlegt werden.
    Das geschieht mit "index.data(Qt.ItemDataRole.UserRole+1000)" (beim lesen) und "setData(index.data(Qt.ItemDataRole.UserRole+1000), prozent)" beim schreiben.
    Noch kenne ich keinen Weg, die häßliche grüne Farbe des Chunk zu ändern ...
    rg, 2021-07-25
    """

    def paint(self, painter, option, index):
        progress = index.data(Qt.ItemDataRole.UserRole + 1000)
        if progress is None:
            progress = 0
        opt = QStyleOptionProgressBar()
        opt.rect = option.rect
        opt.chunk = QColor(210, 105, 30)
        opt.textAlignment = Qt.AlignmentFlag.AlignCenter
        opt.minimum = 0
        opt.maximum = 100
        opt.progress = progress
        opt.text = f"{progress}%"
        opt.textVisible = True
        # QApplication.style().drawControl(
        #     QStyle.ControlElement.CE_ProgressBar, opt, painter
        opt.state |= QStyle.StateFlag.State_Horizontal
        style = (
            option.widget.style() if option.widget is not None else QApplication.style()
        )
        style.drawControl(
            QStyle.ControlElement.CE_ProgressBar, opt, painter, option.widget
        )
        print("Nach drawControl")


class Fortschritt:
    # Klasse, um die Statistik einer Konvertierung aufzufangen
    # Die Funkion 'fortschritt_speichern' gibt zurück:
    #   - True:  wenn der letzte Posten 'progress' erkannt wurde
    #   - False: wenn gespeichert wurde, aber nicht 'progress' erschien
    #   - None:  wenn irgend etwas unverdauliches auftauchte

    # parmListe = ['frame', 'fps', 'stream_0_0_q', 'bitrate', 'total_size', 'out_time_us',
    parmListe = [
        "frame",
        "fps",
        "bitrate",
        "total_size",
        "out_time_us",
        "out_time_ms",
        "out_time",
        "dup_frames",
        "drop_frames",
        "speed",
        "progress",
    ]

    def __init__(self):
        self.pwDic = dict()
        for parm in self.parmListe:
            self.pwDic[parm] = ""

    def fortschritt_speichern(self, zeile):
        """speichert ein "NAME=WERT" Paar ab"""
        if not "=" in zeile:
            return None

        pwListe = zeile.split("=")
        if not len(pwListe) == 2:
            return None

        parm, wert = pwListe

        if parm in self.parmListe:
            self.pwDic[parm] = wert

        if re.search(
            r"stream_\d_\d_q", parm
        ):  # Ausdrücke wie "stream_0_0_q" oder "stream_0_1_q"
            self.pwDic["q"] = wert

        if parm == "progress":  # explicit is better than implicit
            return True
        else:
            return False

    def getParm(self, parm):
        if parm not in self.parmListe:
            return None
        else:
            return self.pwDic[parm]

    def fortschritt_fomatieren(self):

        try:
            sz = int(self.pwDic["total_size"])
        except:
            sz = 99
        szt = f"{sz:,}".replace(",", ".")
        txt = f">  frame={self.pwDic['frame']}   fps={self.pwDic['fps']}   q={self.pwDic['q']}   size={szt}   time={self.pwDic['out_time']}   bitrate={self.pwDic['bitrate']}   speed={self.pwDic['speed']}"
        return txt


class XCodeApp(QMainWindow, XCodeUI.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.setupUi(self)  # This is defined in XCodeUI.py file automatically
        # It sets up layout and widgets that are defined

        # Instanz-Variablen
        self.ff = ffcmd.ffmpegcmd()
        self.frameCount = 0
        self.lastFrameInfo = ""
        self.saveTxt = ""  # für -onReadData
        self.saveTxtAnz = 0  # für -onReadData
        self.fortschritt = (
            None  # hält das Fortschritt Objekt des aktuell codierten Film
        )
        self.process = None
        self.processkilled = False
        self.currentX = True  # Zustamd der X-Spalte; True=alle aktiviert
        self.quelle = Konstanten.QUELLE
        self.ziel = Konstanten.ZIEL
        self.logpath = Konstanten.LOGPATH
        self.tsliste = liste.liste()  # Liste der ts-Objekte
        self.running = False  # im Prozess aktiv
        self.stopNext = False  # HalteSignal
        #        self.Zeile = 0         # aktuelle Zeile (0 - (n-1))
        self.incr = 0.0  # Increment des Procbar1
        self.pbarpos = 0  # Pos des ProcBar1
        self.prstart = 0  # start timer des prozesses
        self.prend = 0  # end timer
        self.ts_von = ""  # aktuelle quelle
        self.ts_nach = ""  # aktuelles ziel
        self.lastcmd = ""  # letzter cmd, der im Prozess verarbeitet wurde
        self.w = None  # externes Transcode Window
        self.redoWithCopy = False  # WiederholungsFlag für nurCopy-Jobs

        # Icon versorgen
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS
        elif __file__:
            application_path = os.path.dirname(__file__)

        self.setWindowIcon(QIcon(os.path.join(application_path, Konstanten.iconFile)))

        # scriptDir = os.path.dirname(os.path.realpath(__file__))
        # self.setWindowIcon(QIcon(scriptDir + os.path.sep + "XC.ico"))
        # self.setWindowIcon(QIcon(scriptDir + os.path.sep + "FLGGERM.ICO"))

        # Feintuning der Widgets
        self.tbl_files.setHorizontalHeaderLabels(
            ("Nr", "X", "Datei", "Typ", "Progress", "Status")
        )
        self.tbl_files.setAlternatingRowColors(True)
        # self.delegate = ProgressDelegate(self.tbl_files)

        # hier stürzt er ab
        # self.tbl_files.setItemDelegateForColumn(4, self.delegate)
        ###### self.tbl_files.setItemDelegateForColumn(4, ProgressDelegate(self.tbl_files))

        # self.tbl_files.setStyleSheet(pbarsheet)

        header = self.tbl_files.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_files.setAlternatingRowColors(True)
        header.setSectionsClickable(True)  # 4 toggle X

        self.lbl_version.setText(
            "XCode Version " + Konstanten.VERSION + " vom " + Konstanten.VERSION_DAT
        )
        self.lbl_frames.setText("")

        self.edit.setWindowTitle("Prozess-Ausgabe")
        self.edit.setText("Benutzte ffcmd.ini:\n\n" + self.ff.usedIni + "\n\n")

        self.led_pfad.setDisabled(True)
        self.probar1.setValue(0)
        self.probar2.setValue(0)

        # connects
        self.btn_ende.clicked.connect(self.progende)
        self.btn_start.clicked.connect(self.convert)
        self.tbl_files.doubleClicked.connect(self.toggleX)
        header.sectionDoubleClicked.connect(self.toggleAllX)

        # Abschluss Init; laden der Daten
        self.dt = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log = logger.logFile(
            self.logpath + "XCode_" + self.dt + ".log", TimeStamp=True, printout=False
        )

        self.log.log("Umwandlung mit:")
        self.log.log(
            self.ff.ffXcodeCmd("{EingabeDatei}", "{AusgabeDatei}", nurLog=True) + "\n"
        )

        if Konstanten.logProgress:
            Konstanten.ffmpegLog = Konstanten.ffmpegLog + "-" + self.dt + ".log"
            with open(Konstanten.ffmpegLog, "a") as flog:
                flog.write("")

        self.ladeFiles(self.quelle)

        if self.tsliste.size == 0:
            reply = QMessageBox.information(
                self,
                "Hinweis",
                "Es gibt im Order {0} keine ts-Dateien.\nNichts zu tun!".format(
                    self.quelle
                ),
            )
            return
        else:
            self.incr = 100.0 / self.tsliste.size
        self.statusbar.showMessage("{0} Dateien geladen!".format(self.tsliste.size))

    def onReadData(self):
        """fängt die Meldungen von ffmpeg ab und bringt sie passen zur anzeige"""
        #
        # -- seqAusgabe.txt
        # frame=0
        # fps=0.00
        # stream_0_0_q=0.0
        # bitrate=   0.0kbits/s
        # total_size=0
        # out_time_us=83438
        # out_time_ms=83438
        # out_time=00:00:00.083438
        # dup_frames=0
        # drop_frames=0
        # speed=0.277x
        # progress=continue
        # ...
        # frame=130183
        # fps=116.69
        # stream_0_0_q=22.0
        # bitrate=1129.7kbits/s
        # total_size=735357590
        # out_time_us=5207520000
        # out_time_ms=5207520000
        # out_time=01:26:47.520000
        # dup_frames=0
        # drop_frames=4
        # speed=4.67x
        # progress=end

        parmListe = [
            "frame",
            "fps",
            "stream_0_0_q",
            "bitrate",
            "total_size",
            "out_time_us",
            "out_time_ms",
            "out_time",
            "dup_frames",
            "drop_frames",
            "speed",
            "progress",
        ]
        # txt = self.process.readAllStandardOutput().data().decode('cp850')
        txt = self.process.readAllStandardOutput().data().decode("cp1252")
        if Konstanten.logProgress:
            # jeder Block wird mit einem §\n abgeschlossen, jedes \r wird durch $ sichtbar gemacht
            with open(Konstanten.ffmpegLog, "a") as flog:
                try:
                    tx = txt.replace("\r", "$")
                except:
                    tx = txt
                flog.write(tx)
                flog.write("§\n")

        txt = txt.replace("\r", "\n")
        zeilen = txt.split("\n")
        for zeile in zeilen:
            if zeile == "":
                continue
            pos = zeile.find("=")
            erg = None
            if (len(zeile) < 33) and (pos > 0):  # out_time_us=-9223372036854775807
                p = zeile[:pos]
                if p in parmListe:
                    # ggf. einen wirren rest abschneiden
                    if p == "frame":
                        # eine leerstelle nach dem wert, wie bei 'zeile ='frame= 1208 fps=594 q=29.0 size=   12288kB'
                        if (leer := zeile.find(" ", 11)) > -1:
                            zeile = zeile[:leer]
                            # print(f"HIT {zeile =}; {leer =}; {pos=}")
                    # print(f"{zeile=}")
                    erg = self.fortschritt.fortschritt_speichern(zeile)
                    # print(f"{p =} in parmListe, {erg =}")
                else:
                    # print(f"{p =} NICHT in parmListe, {erg =}")
                    if not zeile.startswith("frame="):
                        self.infoZeilenAusgeben(zeile)
                if erg == True:
                    self.anzeigeFortschritt()
            else:  # kein = gefunden oder zeile zu lang
                if zeile > "" and not zeile.startswith("frame="):
                    self.infoZeilenAusgeben(zeile)
        return

    def infoZeilenAusgeben(self, zeile):
        """
        gibt die InfoZeilen im Fenster self.edit aus
        Parm:
            zeile:  der Text, der ausgegeben werden soll (kann auch Blank sein)
        """
        zeile = zeile.strip()
        if zeile.find("\r") > -1:
            zeile = zeile.replace("\r", "\n")
        if zeile > "":
            edt = self.edit.toPlainText()
            self.edit.setText(edt + zeile + "\n")
            self.edit.moveCursor(QTextCursor.MoveOperation.End)
            # with open("debug.Log", "a") as flog:
            #     flog.write(zeile.replace("\r", "$"))
            #     flog.write('§\n')

        return

    def anzeigeFortschritt(self):
        try:
            anzFrames = int(self.fortschritt.getParm("frame"))
        except:
            anzFrames = None
            return
        if anzFrames > self.frameCount:
            anzFrames = self.frameCount
        # if not self.frameCount:
        #     print(f"{frameCount=}")

        proD = anzFrames / self.frameCount
        proI = int(proD * 100)

        # Anzeige der Position
        self.probar2.setValue(anzFrames)
        pb1wert = self.pbarpos + proD * self.incr
        self.probar1.setValue(round(pb1wert))

        row = self.tsliste.lastPos
        itm = self.tbl_files.item(row, 4)
        itm.setData(Qt.ItemDataRole.UserRole + 1000, proI)
        itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # change the alignment
        itm.setText(f"{proD*100:3.2f}" + " %")
        self.tsliste.lastObj.progress = proI
        txt = self.fortschritt.fortschritt_fomatieren()
        self.lbl_frames.setText(txt)
        self.lastFrameInfo = txt

    def toggleAllX(self, index):
        """schaltet alle X an oder aus"""
        if index != 1:
            return
        # header = self.tbl_files.horizontalHeader()
        # if not header.sectionDoubleClicked(1):
        #     # if not idx == 1:
        #     return
        for row in range(self.tsliste.size):
            Datei = self.tsliste.getRow(row)
            if Datei is None:
                return
            else:
                Datei.toggleXObj()
                self.refreshTableRow(row)  # kein Neuaufbau
                self.tbl_files.selectRow(row)
        return

    def toggleX(self):
        """schaltet das X einer einzigen Zeile um"""
        # zunächst die aktuelle Zeile finden
        idx = self.tbl_files.selectedIndexes()[0]
        row = idx.row()
        # print(f"{idx=}")
        Datei = self.tsliste.getRow(row)
        if Datei is None:
            return
        else:
            Datei.toggleXObj()
            self.refreshTableRow(row)  # kein Neuaufbau
            self.tbl_files.selectRow(row)
            # self.refreshTable(False)    # kein neuaufbau
        return

    def onFinished(self, exitCode, exitStatus):
        self.prend = timer()
        self.running = False
        #
        # print("Vorbei")
        m, s = divmod(self.prend - self.prstart, 60)
        h, m = divmod(m, 60)
        time_str = "{0:02.0f}:{1:02.0f}:{2:02.0f}".format(h, m, s)
        Datei = self.tsliste.lastObj
        if not Datei.X == "X":
            self.log.log(f">>> {Datei.nr} - {Datei.name} übersprungen!")
            if self.tsliste.findNext() is None:
                self.ende_verarbeitung()  # fertig
            else:
                self.convert()  # nächste Datei
                return

        # print("Finished; exitCode={0}, exitStatus={1}".format(exitCode, exitStatus))
        if exitCode == 0:
            try:
                qlen = os.stat(self.ts_von).st_size
            except:
                qlen = 0
            try:
                zlen = os.stat(self.ts_nach).st_size
            except:
                zlen = 0
            Datei.org_len = qlen
            Datei.xcode_len = zlen

            # # 4 test only ---------------------
            # with open("C:\\ts\\lastFrameInfo.info", mode="+bw") as out:
            #     out.write(bytes(self.lastFrameInfo, "utf8"))
            # # 4 test only ---------------------
            fi = self.lastFrameInfo.strip().split("\n")
            frameInf = ""
            for fiz in fi:
                if frameInf:
                    frameInf = frameInf + "\n"
                frameInf = frameInf + ">>> " + fiz
            self.log.log(f"KodierInfo: \n{frameInf}")

            self.log.log(
                "Größen : {0} --> {1} ({2:2.2f}%)".format(
                    format_size(qlen), format_size(zlen), zlen / qlen * 100
                )
            )
            self.log.log(
                "Dauer  : {0}; ExitCode: {1}; ExitStatus: {2} ".format(
                    time_str, exitCode, exitStatus
                )
            )

            # missglückte Konvertierung durch reine Copy korrigieren
            # z.B. das Ergebnis ist Größer als die Quelle
            if zlen >= qlen:
                self.log.log(
                    "\nMisslungene Konvertierung: Das Ziel ist größer als die Quelle!\nVersuche eine reine Copy!"
                )
                self.redoWithCopy = True
                self.convert()
                return

            try:
                shutil.move(self.ts_von, self.ts_von + ".done")
                self.ts_von = self.ts_von + ".done"
            except:
                self.log.log(
                    "Warnung: Konnte die QuelleDatei nicht in *.done umbenennen!"
                )
            self.log.log("OK\n")
            Datei.setStatus("OK")

        else:
            Datei.setStatus("Fehler {0} / {1}".format(exitCode, exitStatus))
            if self.processkilled:
                self.log.log(
                    "Harter Abbruch! exitCode={0}, exitStatus={1}".format(
                        exitCode, exitStatus
                    )
                )
                return  # keine weitere Verarbeitung
            else:
                self.log.log(
                    "Fehler! exitCode={0}, exitStatus={1}".format(exitCode, exitStatus)
                )

        # Abschluss-Arbeiten des aktuellen Prozesses
        # self.edit.setText(" ")
        self.edit.setText("Benutzte ffcmd.ini:\n\n" + self.ff.usedIni + "\n\n")
        self.refreshTable(False)
        self.process = None

        self.probar2.setRange(0, 1)  # stoppt hin-her
        self.probar2.setValue(0)  # ende der Anzeige

        # weitermachen oder aufhören
        if self.stopNext:  # sofort aufhören
            self.ende_verarbeitung()
            return

        # den Fortschrittsbalken abschließen
        row = self.tsliste.lastPos
        itm = self.tbl_files.item(row, 4)
        itm.setData(Qt.ItemDataRole.UserRole + 1000, 100)
        self.tsliste.lastObj.progress = 100
        self.pbarpos += self.incr
        self.probar1.setValue(round(self.pbarpos))

        # neuen Satz aussuchen
        if self.tsliste.findNext() is None:
            self.ende_verarbeitung()  # fertig
        else:
            self.convert()  # nächste Datei

    def closeEvent(self, event):
        if self.running:
            if self.stopNext:
                reply = QMessageBox.warning(
                    self,
                    "Achtung!",
                    "Laufende Konvertierung abbrechen?\nDas macht die neu erzeugte Ausgabe unbrauchbar!",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
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
        itm.setData(Qt.ItemDataRole.UserRole + 1000, zahl)
        self.tsliste.lastObj.progress = zahl

    # Funktionen

    def ladeFiles(self, ts_pfad):  # lädt die ts-Files
        ladeWin = ladeFenster(self)
        ladeWin.show()
        # Liste der ts-files laden
        i = 0
        for entry in os.scandir(ts_pfad):
            if entry.is_file():
                fname, fext = os.path.splitext(entry.name)
                if fext in [".ts", ".mpg", ".mp4", ".mkv", ".mv4", ".mpeg", ".avi"]:
                    i += 1
                    fullpath = os.path.join(ts_pfad, entry.name)
                    ladeWin.setZeile(f"({i}) - {fullpath}")
                    tse = tsEintrag(i, fullpath, entry.name, fext, "warten...  ")
                    self.tsliste.append(tse)
                    self.log.log("Lade: {0:2}: {1}".format(i, entry.name))
        self.tsliste.findFirst()
        self.refreshTable(True)
        ladeWin.close()
        return self.tsliste.size

    def refreshTable(self, neuaufbau):
        # das Table-widget füllen
        if neuaufbau:
            self.tbl_files.setRowCount(0)
        for ts in self.tsliste.liste:
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
                itm.setData(Qt.ItemDataRole.UserRole + 1000, 0)
                self.tbl_files.setItem(nr, 5, QTableWidgetItem(ts.status))
                # zentrieren
                itm = self.tbl_files.item(nr, 0)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                itm = self.tbl_files.item(nr, 1)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                itm = self.tbl_files.item(nr, 3)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                itm = self.tbl_files.item(nr, 5)
                itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                if nr == self.tsliste.lastPos:
                    self.tbl_files.setItem(nr, 1, QTableWidgetItem(ts.X))
                    itm = self.tbl_files.item(nr, 1)
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    itm = self.tbl_files.item(nr, 4)
                    itm.setData(Qt.ItemDataRole.UserRole + 1000, ts.progress)
                    self.tbl_files.setItem(nr, 5, QTableWidgetItem(ts.status))
                    itm = self.tbl_files.item(nr, 5)
                    itm.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
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

    def convert(self):
        """
        konvertiert eine ts-Datei über einen separaten Prozess
        """
        row = self.tsliste.lastPos
        Datei = self.tsliste.lastObj
        # keine Verarbeitung, falls kein X gesetzt wurde
        if not Datei.X == "X":
            Datei.setStatus("skipped")
            self.onFinished(0, 0)
            return

        # GUI anpassen
        self.probar1.setValue(round(self.pbarpos))
        self.btn_start.setEnabled(False)

        Datei.setStatus("läuft...")
        self.refreshTable(False)
        self.tbl_files.selectRow(row)
        fname, _ = os.path.splitext(Datei.name)
        self.ts_nach = self.ziel + fname + ".mkv"
        self.ts_von = Datei.fullpath
        self.log.log("\nStart Konvertierung von {0} . . .".format(self.ts_von))
        self.log.log(
            f"Auflösung: {Datei.video.typ} ({Datei.video.weite} x {Datei.video.hoehe})"
        )
        self.statusbar.showMessage(
            "Umwandlung {0} -> {1}".format(self.ts_von, self.ts_nach)
        )

        # -----------------------------------------------------------------------------
        # cmd montieren
        if self.redoWithCopy:
            Datei.copyMode = True
        self.lastcmd = self.ff.ffXcodeCmd(
            self.ts_von, self.ts_nach, nurCopy=self.redoWithCopy
        )
        self.redoWithCopy = False
        self.frameCount = Datei.video.frameCount
        self.fortschritt = Fortschritt()
        self.log.log("ffmpeg Aufruf: {0}".format(self.lastcmd))
        self.statusbar.showMessage(
            "Umwandlung {0} -> {1}".format(self.ts_von, self.ts_nach)
        )

        if self.frameCount == 0:
            self.probar2.setTextVisible(False)
            self.probar2.setRange(0, 0)  # start hin-her
            self.probar2.setValue(0)
        else:
            self.probar2.setTextVisible(True)
            self.probar2.setRange(0, self.frameCount)
            self.probar2.setFormat("%v")
            self.probar2.setValue(0)

        # # Prozess starten
        self.running = True
        self.prstart = timer()
        self.process = QProcess()
        self.process.finished.connect(self.onFinished)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.onReadData)
        self.process.start(self.lastcmd)
        if Konstanten.logProgress:
            with open(Konstanten.ffmpegLog, "a") as flog:
                flog.write(
                    f"\n---------- [{self.ts_von}] ------------------------------------\n"
                    + "Das Ende eines eingelesenen Blocks wird mit '§CRLF' gekennzeichnet,"
                    + "Ein einfaches 'CR' wird mit '$' markiert"
                    + "-" * 80
                )

    def progende(self):  # Ende Proc mit Nachfrage
        if self.running:
            if self.stopNext:
                self.processkilled = True
                self.close()
            else:
                reply = QMessageBox.question(
                    self,
                    "Nachfrage",
                    "Ablauf abbrechen?\n\nJa = Das wird nach dem Ende der aktuellen Konvertierung geschehen!\n\nNein = weitermachen\n\nCANCEL = sofortiger harter Abbruch!!",
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                    | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.stopNext = True
                    self.statusbar.showMessage(
                        "Die Konverierung endet nach dem aktuellen Prozess!"
                    )
                    self.btn_ende.setText("Sofort beenden")
                    self.btn_ende.setDisabled(False)
                elif reply == QMessageBox.StandardButton.Cancel:
                    self.processkilled = True
                    self.ende_verarbeitung()
                else:
                    pass  # nix abzubrechen
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
                self.process.waitForFinished(10000)
                if os.path.isfile(self.ts_nach):  # die defekte Datei löschen
                    try:  # versuchen, die kaputte *.mkv"-datei zu löschen
                        os.remove(self.ts_nach)
                    except:
                        QMessageBox.information(
                            self,
                            "Achtung!",
                            "Die defekte Datei \n{0}\nkonnte NICHT gelöscht werden!".format(
                                self.ts_nach
                            ),
                        )
                        self.log.log(
                            "Defekte Zieldatei [{0}] konnte NICHT gelöscht werden!"
                        )
                    else:
                        self.log.log("Defekte Zieldatei wurde gelöscht!")
                self.log.log("Harter Abbruch!")
                txt = "Harter Abbruch!"
            elif self.stopNext:
                txt = "Die Verarbeitung wurde nach Anforderung vorzeitig beendet!"
                self.log.log("Ende nach Abbruch!")
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
        anzCopyMode = 0
        summe_org = 0
        summe_xcode = 0
        for ts in self.tsliste.liste:
            if ts.copyMode:
                anzCopyMode += 1
            if ts.status == "OK":
                ok += 1
                summe_org += ts.org_len
                summe_xcode += ts.xcode_len
            elif ts.status == "warten...  ":
                wait += 1
            elif ts.status == "skipped":
                skipped += 1
            else:
                err += 1
        if (wait == 0) & (err == 0) & (ok > 0):
            txt = (
                f"\nTransCode OK!\n\nOK: {ok}\n"
                + f"davon nur kopiert: {anzCopyMode}\n"
                + f"Fehler: {err}\n"
                + f"Nicht bearbeitet: {wait + skipped}\n"
            )
            isOK = True
        else:
            txt = (
                f"\nErgebnis!\n\nOK: {ok}\n"
                + f"davon nur kopiert: {anzCopyMode}\n"
                + f"Fehler: {err}\n"
                + f"Nicht bearbeitet: {wait + skipped}\n"
            )
            isOK = False
        summe_org_str = format_size(summe_org)
        summe_xcode_str = format_size(summe_xcode)
        txt = (
            txt
            + "\n"
            + "-" * 80
            + "\n"
            + f"Summe der Quell-Dateien:  {summe_org_str}\n"
            + f"Summe der XCode-Dateien:  {summe_xcode_str}\n"
        )
        if summe_org > 0:
            txt += f"Kompression auf:  {summe_xcode/summe_org*100:.2f}%"
        return (txt, isOK)


def format_size(flen: int):
    """Human friendly file size"""
    unit_list = list(zip(["bytes", "kB", "MB", "GB", "TB", "PB"], [0, 3, 3, 3, 3, 3]))
    if flen > 1:
        exponent = min(int(logarit(flen, 1024)), len(unit_list) - 1)
        quotient = float(flen) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        s = "{:{width}.{prec}f} {}".format(quotient, unit, width=8, prec=num_decimals)
        s = s.replace(".", ",")
        return s
    elif flen == 1:
        return "  1 byte"
    else:  # flen == 0
        return " 0 bytes"


def split_parms(parmStr: str) -> dict:
    """
    Zerlegt einen String der Form:
    "frame=344874 fps=136 q=20.0 Lsize= 3003827kB time=01:54:59.46 bitrate=3566.6kbits/s speed=2.72x"
    in ein Dict, d.h. eine Liste, in der der ParmName der Index ist und der Wert hinter dem "=" der Wert ist
    Das Problem waren die evtl. führenden Blanks der Werte-Angaben, wie hier bei 'Lsize'
    """
    retDict = dict()
    worte = parmStr.split(" ")
    # print(f"{worte =}")
    altParm = ""
    altParmLeer = False
    i = 0
    for wort in worte:
        if wort == "":
            continue
        aktw = wort.split("=")
        if wort.endswith("="):  # der parm fehlt
            altParm = aktw[0]
            altParmLeer = True
            continue
        elif altParmLeer:  # dann muss der wert folgen
            retDict[altParm] = aktw[0].strip()
            altParmLeer = False
        else:  # 'Name=Wert' Typ
            if len(aktw) < 2:
                print("Unpassender String!!")
                print(f"{worte =}")
                print(f"{aktw =} {altParm =}")
                continue
            retDict[aktw[0]] = aktw[1].strip()
            altParmLeer = False
    return retDict


def main():

    StyleSheet = """
QMainWindow {
    background-color: #fff5cc;
}
QTableWidgt {
    background-color: DimGray;
}
#tbl_files {
    border: 1px solid Chocolate;
    border-radius: 5 px;
    }

#led_pfad {
    border: 1px solid Chocolate;
    border-radius: 5 px;
    }

#lbl_version {
    background-color: #fff5cc;
}

#lbl_frames {
    border: 1px solid Chocolate;
    border-radius: 5 px;
    background-color: #E0E0E0;
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
    border-color: Chocolate;
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
    border-color: Chocolate;
    text-align: center
}
#probar2::chunk {
    background-color: Chocolate;
}

QTextEdit {
    color: Black;
    background-color: Gainsboro;
    border: 1px solid Chocolate;
    border-radius: 5px;
}
"""

    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)

    form = XCodeApp()  # We set the form to be our App
    if form.tsliste.size == 0:  # nix zu tun!
        return

    form.show()  # Show the form

    app.exec()  # and execute the app


if __name__ == "__main__":
    main()  # run the main function
