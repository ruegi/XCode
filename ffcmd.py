# -*- coding: utf-8 -*-
"""
Created on Sun, 2019-01-19

@author: rg

Name: ffcmd
laden der ffmpeg-Befehle aus einer Datei und montieren des Transcode-Aufrufs

Änderungen:
2020-02-04  rg      Analyse des Codierung der Quelldatei eingebaut
"""
from pathlib import Path
from os.path import split, splitext
import filmAlyser

class ffmpegcmd:

    def __init__(self):
        head, tail = split(__file__)
        root, ext = splitext(tail)
        if head == "":
            head = "."
        self.initFile = head + "\\" + root + ".ini"
        # print(head, tail, ext, self.initFile)
        # init Command-String für das Transcodieren herstellen oder lesen
        pFile = Path(self.initFile)
        if pFile.is_file():
            with open(self.initFile, "r") as iniFHdl:
                cmd = iniFHdl.read()
        else: # sofort eine default-Ini-Datei mit default Eintrag erzeugen
            cmd = "c:\\ffmpeg\\bin\\ffmpeg -vsync 0 -hwaccel cuvid -c:v {Codierung} -i "
            cmd = cmd + "\"{0}\" ".format("{EingabeDatei}")
            cmd = cmd + '-map 0 -c:v hevc_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset slow -f matroska -y '
            cmd = cmd + "\"{0}\"".format("{AusgabeDatei}")
            with open(self.initFile, "w") as iniFHdl:
                iniFHdl.write(cmd)
        # den aktuellen ffmpeg-Aufruf merken
        self.ffmCmd = cmd

    def ffXcodeCmd(self, ts_von, ts_nach, nurLog=False):
        # veraltet: 
        # das "&" stört unter Windows im Aufruf, es muss maskiert werden
        # nach Tests überflüssig! rg
        # von = ts_von.replace("&", "^&")
        # nach = ts_nach.replace("&", "^&")
        #        cmd = "cmd /C c:\\ffmpeg\\bin\\ffmpeg -i "
        # -
        # die Codierung der QuellDatei eimbauen
        if nurLog:
            return self.ffmCmd
        # zunächst die Codierung herausbekommen       
        codier = filmAlyser.get_encoding(ts_von)
        parm = "h264_cuvid"     # default
        if codier is not None:
            if codier == "h264":
                parm = "h264_cuvid"
            elif codier == "hevc":
                parm = "hevc_cuvid"
            elif codier == "mpg":
                parm = "mpeg2_cuvid"
            else:
                parm = "h264_cuvid" # auf gut Glück...
        cmd = self.ffmCmd.replace("{Codierung}", parm)
        # dann von und nach ersetzen
        # KEINE ERSETZUNG NÖTIG, WENN DER STRING IN ANFÜHRUNGSSTRICHEN STEHT!
        # ts_von = correct_illegal_chars(ts_von)
        # ts_nach = correct_illegal_chars(ts_nach)
        cmd = cmd.replace("{EingabeDatei}", ts_von)
        cmd = cmd.replace("{AusgabeDatei}", ts_nach)
        # print(f"Codier=({codier}), Parm=({parm})")
        return cmd

def correct_illegal_chars(txt:"der zu prüfende String") -> str:
    ''' 
    Maskiert ein & durch ^&; unter win nötig, da cmd sonst falsch interpretiert
    '''
    try:
        i = txt.index("&")        
    except:
        i = None
    if i is not None:
        if i > 0:
            if txt[i-1] == "^":
                pass            # & ist bereits 'escaped'
            else:
                txt = txt.replace("&", "^&")
    return txt
     


if __name__ == '__main__':
    ff = ffmpegcmd()
    von  = "C:\\ts\\Blood_&_Treasure_-_Kleopatras_Fluch_(1-1)_Der_Agent_und_die_Meisterdiebin.ts"
    nach = "E:\\Filme\\schnitt\\Blood_&_Treasure_-_Kleopatras_Fluch_(1-1)_Der_Agent_und_die_Meisterdiebin.mkv"

    cmd = ff.ffXcodeCmd(von, nach)

    print("Eingabe   : {0}".format(von))
    print("Ausgabe   : {0}".format(nach))
    print("----------------------------------------------------------------------")
    print("cmd       : {0}".format(cmd))
    print("Ende")
