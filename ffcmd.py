# -*- coding: utf-8 -*-
"""
Created on Sun, 2019-01-19

@author: rg

Name: ffcmd
laden der ffmpeg-Befehle aus einer Datei und montieren des Transcode-Aufrufs

Änderungen:
2020-02-04  rg      Analyse der Codierung der Quelldatei eingebaut
2023-05-29  rg      videoFile integriert; Codierung der QuellDatei wieder entfernt
"""
from pathlib import Path
# from os.path import split, splitext
import configparser
import videoFile
import os

class Konstanten():
    FFMPEG = r'c:\ffmpeg\bin\ffmpeg.exe'
    ICON = 'XCode.ico'
    INIDATEI = r'.\ffcmd.ini'
    XCODEZIEL = 'E:\\Filme\\schnitt\\'
    LOGPATH = 'E:\\Filme\\log\\'
    SD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 6.2 -tier high -preset p7 -tune hq -dn -codec:a copy -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    HD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 6.2 -tier high -preset p7 -tune hq -dn -codec:a copy -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    FHD_CMD = 'c:\\ffmpeg\\bin\\ffmpeg -hide_banner {canvassize} -hwaccel auto -i "{EingabeDatei}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 6.2 -tier high -rc vbr -cq 28 -qmin 28 -qmax 28 -dn -codec:a aac -c:s dvdsub -y -f matroska "{AusgabeDatei}"'
    MUSTER_FFMCMD = f'''\
[SD]
cmd = {SD_CMD}

[HD]
cmd = {HD_CMD}

[FullHD]
cmd ={FHD_CMD}
# alternative
# fhd_cmd = c:\\ffmpeg\\bin\\ffmpeg -hide_banner {{canvassize}} -hwaccel auto -i "{{EingabeDatei}}" -map 0 -c:v hevc_nvenc -pix_fmt p010le -profile:v main10 -level 6.2 -tier high -preset p7 -tune hq -dn -codec:a aac -c:s dvdsub -y -f matroska "{{AusgabeDatei}}"
'''

class ffmpegcmd:

    def __init__(self):
        # head, tail = split(__file__)
        # root, ext = splitext(tail)
        # if head == "":
        #     head = "."
        # print(head, tail, ext, self.initFile)

        self.video = None
        self.initFile = Konstanten.INIDATEI     # head + "\\" + root + ".ini"
        # init Command-String für das Transcodieren herstellen oder lesen
        pFile = Path(self.initFile)
        if not pFile.is_file():
        #     with open(self.initFile, "r") as iniFHdl:
        #         cmd = iniFHdl.read()
        # else: # sofort eine default-Ini-Datei mit default Eintrag erzeugen            
            cmd = Konstanten.MUSTER_FFMCMD
            with open(self.initFile, "w") as iniFHdl:
                iniFHdl.write(cmd)
        
        # die aktuellen ffmpeg-Aufrufe merken
        config = configparser.ConfigParser()   
        # config.read(self.initFile)['HD']
        
        self.cmd_SD =  config.get('SD', 'cmd', fallback=Konstanten.SD_CMD)
        self.cmd_HD =  config.get('HD', 'cmd', fallback=Konstanten.HD_CMD)
        self.cmd_FullHD = config.get('FullHD', 'cmd', fallback=Konstanten.FHD_CMD)
        self.usedIni = f"[SD]\n{self.cmd_SD}\n\n[HD]\n{self.cmd_HD}\n\n[FullHD]\n{self.cmd_FullHD}\n"


    def ffXcodeCmd(self, ts_von, ts_nach, nurLog=False):
        '''
        montiert den ffmpeg Aufruf
        Parameter:  ts_von: QuellVideo
                    ts_nach: ZielVideo
                    nurLog (opt.): wenn True, wird nur die benutzte Ini-Datei zurückgegeben (ohne Auflösung der Variablen)
        Returns:    den montierten ffmpec Aufruf String
        '''
        if nurLog:
            return "SD:  " + self.cmd_SD + "\nHD:  " + self.cmd_HD + "\nFullHD: " + self.cmd_FullHD

        aufrufDict = {'SD': self.cmd_SD, 'HD': self.cmd_HD, 'FullHD': self.cmd_FullHD, }

        self.video = videoFile.videoFile(ts_von)
        
        if self.video.typ in ("SD", "HD", "FullHD"):
            cmd = aufrufDict[self.video.typ]
        else:
            cmd = aufrufDict["HD"]  # default

        # weitere Ersetzungen der cmd-Zeile
        cmd = cmd.replace("{EingabeDatei}", ts_von)
        cmd = cmd.replace("{AusgabeDatei}", ts_nach)
        # BitRaten-Rechnerei (nach 2021-07-16 nicht mehr erforderlich)
        brs = "0"
        if cmd.find("{BitRate}") > 0:
            cmd = cmd.replace("{BitRate}", self.video.bitRate)

        cmd = cmd.replace("{canvassize}", f"-canvas_size {self.video.weite}x{self.video.hoehe}")

        return cmd
    


# def correct_illegal_chars(txt="der zu prüfende String") -> str:
#     ''' 
#     Maskiert ein & durch ^&; unter win nötig, da cmd sonst falsch interpretiert
#     '''
#     try:
#         i = txt.index("&")        
#     except:
#         i = None
#     if i is not None:
#         if i > 0:
#             if txt[i-1] == "^":
#                 pass            # & ist bereits 'escaped'
#             else:
#                 txt = txt.replace("&", "^&")
#     return txt
     


if __name__ == '__main__':
    film = "Quo_vadis_(1951).ts"
    von  = "C:\\ts\\" + film
    nach = "E:\\Filme\\schnitt\\" + film + ".mkv"

    if os.path.isfile(von):
        video = videoFile.videoFile(von)
    else:
        exit(1)

    ff = ffmpegcmd()
    cmd = ff.ffXcodeCmd(von, nach)

    print("Eingabe   : {0}".format(von))
    print("Ausgabe   : {0}".format(nach))
    print("----------------------------------------------------------------------")
    print("cmd       : {0}".format(cmd))
    print("Ende")
