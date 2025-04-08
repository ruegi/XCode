# -*- coding: utf-8 -*-
"""
Created on Sun, 2019-01-19

@author: rg

Name: ffcmd
laden der ffmpeg-Befehle aus einer Datei und montieren des Transcode-Aufrufs

Änderungen:
2020-02-04  rg      Analyse der Codierung der Quelldatei eingebaut
2023-05-29  rg      videoFile integriert; Codierung der QuellDatei wieder entfernt
2024-06-07  rg      ffcmd Muster aktualisiert
2025-03-08  rg      Abhängigkei von videoFile gelöst; Ersatz von MediaInfo durch ffmpeg-python (ffprobe);
                    Übergabe des Cmd-Strings zusätzlich als Liste (vormals nur als string)
2025-03-24  rg      Die Film-Attribute werden jetzt mittels openCV ermittelt; Grund ist die stabile Angabe der FrameCounts (=nb_fames)
2025-04-07  rg      Zurück zu den Anfängen: ffprobe statt openCV (in getVideoSpecs); openCV hat Probleme beim Kompilieren und ist zu groß
                    Dabei habe ich jetzt den FrameCount , wenn er nicht vorhanden ist, aus der "fps" und der "duration" berechnet;
                    Bei nicht im Film vorhdenen FrameCounts werden diese acuh in openCV aus der avg_framerate und der duration berechnet;
                    das reicht hier aus. Dazu isr ffprobe auch schneller.
"""
# import pprint
from pathlib import Path

import configparser

import os
import sys
import subprocess

# env Logik
from dotenv import dotenv_values

class Konstanten:
    if sys.platform == "win32":
        FFMPEG = r"c:\ffmpeg\bin\ffmpeg.exe"
        INIDATEI = "ffcmd.ini"
        XCODEZIEL = "E:\\Filme\\schnitt\\"
        LOGPATH = "E:\\Filme\\log\\"
    else:   # LINUX
        FFMPEG = "/usr/bin/ffmpeg"
        INIDATEI = "ffcmd.ini"
        XCODEZIEL = "/home/ruegi/Videos/schnitt"
        LOGPATH = "/home/ruegi/Videos/log/"

    # DEFAULTS
    ICON = "XCode.ico"
    SD_CMD = '{FFMPEG}' + ' -hide_banner {canvassize} -loglevel error -i "{EingabeDatei}" -map 0 -c:v libsvtav1 -pix_fmt yuv420p10le -threads 4 -crf 24 -preset 8 -svtav1-params tune=0 -dn -codec:a libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    HD_CMD = '{FFMPEG}' + ' -hide_banner {canvassize} -loglevel error -i "{EingabeDatei}" -map 0 -c:v libsvtav1 -pix_fmt yuv420p10le -threads 4 -crf 27 -preset 8 -svtav1-params tune=0 -dn -codec:a libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    FHD_CMD = '{FFMPEG}' + ' -hide_banner {canvassize} -loglevel error -i "{EingabeDatei}" -map 0 -c:v libsvtav1 -pix_fmt yuv420p10le -threads 4 -crf 31 -preset 8 -svtav1-params tune=0 -dn -codec:a libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    Copy_CMD = '{FFMPEG}' + ' -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v copy -dn -codec:a libopus -af aformat=channel_layouts="7.1|5.1|stereo" -b:a 128k -c:s dvdsub -y -f matroska "{AusgabeDatei}"'

    # alt seit 2024-06-07
    # SD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 4.1 -tier high -preset p7 -tune hq -dn -codec:a copy -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    # HD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 4.1 -tier high -preset p7 -tune hq -dn -codec:a copy -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    # FHD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 4.1 -tier high -preset p7 -tune hq -dn -codec:a aac -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    # Copy_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v copy -dn -codec:a copy -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    MUSTER_FFMCMD = f"""\
[SD]
cmd = {SD_CMD}

[HD]
cmd = {HD_CMD}

[FullHD]
cmd ={FHD_CMD}

# alternative
# fhd_cmd = FFMPEG + " -hide_banner {{canvassize}} -hwaccel auto -i "{{EingabeDatei}}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 4.1 -tier high -preset p7 -tune hq -dn -codec:a aac -c:s dvdsub -y -f matroska "{{AusgabeDatei}}"

[Copy]
cmd ={Copy_CMD}
"""

# def wertAusDictLesen(dict: dict, key: str):
#     # liest den Wert aus dem 'dict' mit 'key' und gibt ihn zurück;
#     # fängt dabei ggf. einen KeyError ab und gibt dann None zurück
#     try:
#         wert = dict[key]
#     except KeyError:
#         return None
#     return wert


# def getVideoSpecs(ts_von:str)->dict|None:
#     '''
#     liest die Eigenschaften 'bitRate, 'weite', 'hoehe', 'typ', 'frameCnt' und 'duration' aus der VideoDatei aus
#     und gibt sie als Dict zurück;
#     existiert die Datei nicht, wird None zurückgeliefert
#     Benutzt openCV!
#     Dict Keys
#     -------------
#     "bitrate"       int         avg_bitrate
#     "duration"      float       secs.microsecs
#     "weite"         int
#     "hoehe"         int
#     "typ"           str         "SD", "HD", FullHD", "4K"
#     "frameCnt"     int|None    ggf. None!
#     "fps"           int
#     -------------
#     rg, 2025-03-24
#     '''
#     def toInt(wert):
#         try:
#             i = int(wert)
#         except ValueError:
#             i = 0
#         return i

#     if not os.path.exists(ts_von):
#         return None
#     # else:
#     #     print(ts_von)
#     ret = {}
#     cap = cv2.VideoCapture(ts_von)        # dieser Aufruf erzeugt ggf. Fehlermeldungen beim Open des VideoStreams
#     # cap = cv2.VideoCapture(               # diese Varainte funktioniert leider nicht
#     #     ts_von,
#     #     apiPreference=cv2.CAP_FFMPEG,  # was previously cv2.CAP_ANY
#     #     params=[cv2.OPENCV_LOG_LEVEL, 0],   # 0 = cv2.LOG_LEVEL_SILENT
#     # )
#     frameCnt= toInt(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     ret["frameCnt"] = frameCnt
#     ret["weite"] = toInt(cap.get(cv2.CAP_PROP_FRAME_WIDTH ))
#     ret["hoehe"] = toInt(cap.get(cv2.CAP_PROP_FRAME_HEIGHT ))
#     ret["bitrate"] = toInt(cap.get(cv2.CAP_PROP_BITRATE ))
#     fps = float(cap.get(cv2.CAP_PROP_FPS ))
#     ret["fps"] = fps
#     ret["duration"] = frameCnt / fps
#     ret["typ"] = getVideoTyp(ret["weite"])
#     cap.release()
#     # print("--------------------")
#     # pprint.pprint(ret)

#     return ret

def getVideoSpecs(videoname: str)->dict:
    '''
    benutzt:
        'ffprobe -v error -hide_banner -of default=noprint_wrappers=0 -print_format ini -select_streams v:0 -show_streams "$1"'

    diese Dict Keys werden als Return Value Dict zurückgeliefert:
    -------------
    "bitrate"       int         avg_bitrate
    "duration"      float       secs.microsecs
    "weite"         int
    "hoehe"         int
    "typ"           str         "SD", "HD", FullHD", "4K"
    "frameCnt"     int|None    ggf. None!
    "fps"           int
    -------------
    '''

    def _getVideoType(width: int, height: int) -> str:
        if width >= 3840 and height >= 2160:
            return "4K"
        elif width >= 1920 and height >= 1080:
            return "FullHD"
        elif width >= 1280 and height >= 720:
            return "HD"
        else:
            return "SD"

    cmd = f'ffprobe -v error -hide_banner -of default=noprint_wrappers=0 -print_format ini -select_streams v:0 -show_streams "{videoname}"'
    pobj = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=10, encoding="utf-8")
    if pobj.returncode:
        return None

    # pobj.stdout verarbeiten
    details = {}
    lines = pobj.stdout.splitlines()
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            details[key.strip()] = value.strip()

    # Konvertiere die Werte in die entsprechenden Typen
    erg = {}
    if  "bitrate" in details:
        erg["bitrate"]= int(details["bit_rate"]) // 1000
    else:
        erg["bitrate"] = None
    if "duration" in details:
        erg["duration"] = float(details["duration"])
    else:
        erg["duration"] = None
    if "width" in details:
        erg["weite"] = int(details["width"])
    else:
        erg["weite"] = None
    if "height" in details:
        erg["hoehe"] = int(details["height"])
    else:
        erg["hoehe"] = None

    if erg["weite"] and erg["hoehe"]:
        erg["typ"] = _getVideoType(int(details["width"]), int(details["height"]))
    else:
        erg["typ"] = "HD"


    if "avg_frame_rate" in details:
        erg["fps"] = int(details["avg_frame_rate"].split("/")[0]) // int(details["avg_frame_rate"].split("/")[1])
    else:
        erg["fps"] = None

    if "duration" in details:
        erg["duration"] = float(details["duration"])
    else:
        erg["duration"] = None

    if not "nb_frames" in details or details["nb_frames"] == "N/A":
        if "fps" in erg and "duration" in erg:
            erg["frameCnt"] = int(erg["duration"] * erg["fps"])
        else:
            erg["frameCnt"] = None
    else:
        erg["frameCnt"] = int(details["nb_frames"])

    # gib das Ergebnis zurück
    return erg

class ffmpegcmd:

    def __init__(self):

        config = dotenv_values(".env.xcode")
        Konstanten.FFMPEG = config["FFMPEG"]
        Konstanten.XCODEZIEL = config["ZIEL"]
        Konstanten.INIDATEI = config["INIDATEI"]
        Konstanten.LOGPATH = config["LOGPATH"]

        # print(f"ffmpegcmd: {Konstanten.FFMPEG=}, {Konstanten.XCODEZIEL=}, {Konstanten.INIDATEI=}, {Konstanten.LOGPATH=}")

        self.initFile = Konstanten.INIDATEI  # head + "\\" + root + ".ini"
        # init Command-String für das Transcodieren herstellen oder lesen
        pFile = Path(self.initFile)
        if not os.path.isfile(self.initFile):
        # zur Not, wenn es keine INI-Datei gibt, diese hier erzeugen
            cmd = Konstanten.MUSTER_FFMCMD
            with open(self.initFile, "w") as iniFHdl:
                iniFHdl.write(cmd)

        # die aktuellen ffmpeg-Aufrufe merken
        config = configparser.ConfigParser()
        config.read(self.initFile)

        self.cmd_SD = config.get("SD", "cmd", fallback=Konstanten.SD_CMD)
        self.cmd_HD = config.get("HD", "cmd", fallback=Konstanten.HD_CMD)
        self.cmd_FullHD = config.get("FullHD", "cmd", fallback=Konstanten.FHD_CMD)
        # 4K not yet implemented, but prepared here
        self.cmd_4K = config.get("FullHD", "cmd", fallback=Konstanten.FHD_CMD)
        # config.get('Copy', 'cmd', fallback=Konstanten.HD_Copy)
        self.cmd_Copy = config.get("Copy", "cmd", fallback=Konstanten.Copy_CMD)
        self.usedIni = f"[SD]\n{self.cmd_SD}\n\n[HD]\n{self.cmd_HD}\n\n[FullHD]\n{self.cmd_FullHD}\n\n[Copy]\n{self.cmd_Copy}\n"


    def lstReplace(self, myLst: [], von: str, zu: str, listInsert=False)->[]:
        # Ändert den Eintrag 'von' der Liste myLst in 'zu' \\in Place\\
        # findet nur das erste Vorkommen des Strings 'von'
        # ist listInsert=True, so wird VOR das gefundene Element eingefügt
        try:
            i = myLst.index(von)
            if listInsert:
                myLst.insert(i, zu)
            else:
                myLst[i] = zu
        except ValueError:
            pass


    def ffXcodeCmd(self, ts_von, ts_nach, nurLog=False, nurCopy=False):
        """
        montiert den ffmpeg Aufruf
        Parameter:  ts_von: QuellVideo
                    ts_nach: ZielVideo
                    nurLog (opt.): wenn True, wird nur die benutzte Ini-Datei zurückgegeben (ohne Auflösung der Variablen)
                    nurCopy(opt.): nutzt die self.CMD_Copy, wenn True
                                    (das ist ein FallBack, z.B. wenn das transcodierte Video größer als das Original ist;
                                     z.B. ist das mitunter bei AV1 der Fall)
        Returns:    den montierten ffmpec Aufruf String
        """
        if nurLog:
            # gibt nur das benutzte Set an Ini-Templates ohne Ersetzungen zurück
            return (
                "SD:  "
                + self.cmd_SD
                + "\nHD:  "
                + self.cmd_HD
                + "\nFullHD: "
                + self.cmd_FullHD
            )

        aufrufDict = {
            "SD": self.cmd_SD,
            "HD": self.cmd_HD,
            "FullHD": self.cmd_FullHD,
            "Copy": self.cmd_Copy,
        }

        videoDict = getVideoSpecs(ts_von)

        if nurCopy == True:
            cmd = self.cmd_Copy
        else:
            if videoDict["typ"] in ("SD", "HD", "FullHD"):
                cmd = aufrufDict[videoDict["typ"]]
            else: # Default
                cmd = aufrufDict["HD"]  # default

        cmdLst = cmd.split(" ")     # Liste der einzelnen Parameter des ffmpeg Aufrufs

        cmd = cmd.replace("{FFMPEG}", Konstanten.FFMPEG)
        self.lstReplace(cmdLst, '{FFMPEG}', Konstanten.FFMPEG)

        # weitere Ersetzungen der cmd-Zeile
        cmd = cmd.replace("{EingabeDatei}", ts_von)
        # self.lstReplace(cmdLst, '"{EingabeDatei}"', '"' + ts_von + '"')
        self.lstReplace(cmdLst, '"{EingabeDatei}"', ts_von)

        cmd = cmd.replace("{AusgabeDatei}", ts_nach)
        # self.lstReplace(cmdLst, '"{AusgabeDatei}"', '"' + ts_nach + '"')
        self.lstReplace(cmdLst, '"{AusgabeDatei}"', ts_nach)
        # BitRaten-Rechnerei (nach 2021-07-16 nicht mehr erforderlich)
        brs = "0"
        if cmd.find("{BitRate}") > 0:
            cmd = cmd.replace("{BitRate}", videoDict["bitRate"])
            self.lstReplace(cmdLst, "{BitRate}", videoDict["bitRate"])

        canvasParm = f"{videoDict["weite"]}x{videoDict["hoehe"]}"
        cmd = cmd.replace("{canvassize}", "-canvas_size " + canvasParm)
        self.lstReplace(cmdLst, "{canvassize}", canvasParm)
        self.lstReplace(cmdLst, canvasParm, "-canvas_size", listInsert=True)

        # zum Schluss noch den Progress-Indikator einbauen
        pos = cmd.find(" -i ")
        p1 = cmd[0:pos]
        p2 = cmd[pos:]
        cmd = p1 + " -progress pipe:1 " + p2
        self.lstReplace(cmdLst, "-i", "pipe:1", listInsert=True)
        self.lstReplace(cmdLst, "pipe:1", "-progress", listInsert=True)
        # print(f"{cmd =}")
        # print(f"{cmdLst=}")
        return (cmd, cmdLst)


if __name__ == "__main__":
    # film = "Annika_-_Mord_an_Schottlands_Küste_(S03E06).Annikas_Vater.ts"
    # film = "Annika_-_Mord_an_Schottlands_Küste_(S01E04)_Enthüllungen.mp4.done"
    # film = "Annika_-_Mord_an_Schottlands_Küste_(S03E05)_Wahre_Werte.ts"
    # von = "/home/ruegi/Videos/ts/" + film + ".ts"
    # film = "2012_(2009).ts"
    # film = "Luther (2003).ts.done"
    film = "Leonard_Cohen_-_Live_in_London_(2010).ts.done"
    von = "/home/ruegi/Videos/ts/" + film
    nach = "/home/ruegi/Videos/schnitt/" + film + ".mkv"

    ff = ffmpegcmd()
    cmd = ff.ffXcodeCmd(von, nach, nurCopy=False)

    # print(Konstanten.FFMPEG)

    print("Eingabe   : {0}".format(von))
    print("Ausgabe   : {0}".format(nach))
    print("----------------------------------------------------------------------")
    print("cmd       : {0}".format(cmd[0]))
    print("cmdLst    : {0}".format(cmd[1]))
    print("Ende")
