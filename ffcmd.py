# -*- coding: utf-8 -*-
"""
Created on Sun, 2019-01-19

@author: rg

Name: ffcmd
laden der ffmpeg-Befehle aus einer Datei und montieren des Transcode-Aufrufs

Änderungen:
2020-02-04  rg      Analyse der Codierung der Quelldatei eingebaut
"""
from pathlib import Path
from os.path import split, splitext
import configparser
import filmAlyser

muster_ffcmd = '''\
[SD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset fast -profile:v main10 -pix_fmt p010le -crf 28 -b:v 0 -maxrate 2M -bufsize 4M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"

[HD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 3M -bufsize 6M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"

[FullHD]
cmd = ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 4M -bufsize 8M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"
'''

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
        if not pFile.is_file():
        #     with open(self.initFile, "r") as iniFHdl:
        #         cmd = iniFHdl.read()
        # else: # sofort eine default-Ini-Datei mit default Eintrag erzeugen            
            cmd = muster_ffcmd
            with open(self.initFile, "w") as iniFHdl:
                iniFHdl.write(cmd)
        
        # die aktuellen ffmpeg-Aufrufe merken
        config = configparser.ConfigParser()   
        config.read(self.initFile)
        self.cmd_SD =  config.get('SD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset fast -profile:v main10 -pix_fmt p010le -crf 28 -b:v 0 -maxrate 2M -bufsize 4M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')        
        self.cmd_HD =  config.get('HD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 3M -bufsize 6M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')
        self.cmd_FullHD = config.get('FullHD', 'cmd', fallback='ffmpeg -hide_banner -hwaccel auto -i "{EingabeDatei}"  -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -b:v 0 -maxrate 4M -bufsize 8M -dn -c:a copy -c:s dvdsub -y "{AusgabeDatei}"')


    def ffXcodeCmd(self, ts_von, ts_nach, ts_weite, nurLog=False):
        # veraltet: 
        # das "&" stört unter Windows im Aufruf, es muss maskiert werden
        # nach Tests überflüssig! rg
        # von = ts_von.replace("&", "^&")
        # nach = ts_nach.replace("&", "^&")
        #        cmd = "cmd /C c:\\ffmpeg\\bin\\ffmpeg -i "
        # -
        # die Codierung der QuellDatei eimbauen
        if nurLog:
            return "SD:  " + self.cmd_SD + "\nHD:  " + self.cmd_HD + "\nFullHD: " + self.cmd_FullHD
        # zunächst die Codierung herausbekommen       

        # codier, weite, hoehe = filmAlyser.get_encoding(ts_von)
        
        parm = "HD"     # default
        try:
            iWeite  = int(ts_weite)
        except:
            iWeite = 768

        if iWeite < 1280:
            parm = "SD"
            cmd = self.cmd_SD
        elif iWeite < 1920:
            parm = "HD"
            cmd = self.cmd_HD
        else:
            parm = "FullHD"
            cmd = self.cmd_FullHD

        # wietere Ersetzungen der cmd-Zeile
        cmd = cmd.replace("{EingabeDatei}", ts_von)
        cmd = cmd.replace("{AusgabeDatei}", ts_nach)
        # BitRaten-Rechnerei (nach 2021-07-16 nicht mehr erforderlich)
        brs = "0"
        if cmd.find("{BitRate}") > 0:
        #     bri = int(bitrate)
        #     bri = int(round(bri / (1024*1024) + 0.5, 0))
        #     if bri > 10:
        #         brs = "5M"
        #     elif bri > 6:
        #         brs = "3M"
        #     else:
        #         brs = "0"
            cmd = cmd.replace("{BitRate}", brs)      
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
    # von  = "C:\\ts\\Deutschland,_24_Stunden.ts.done"
    von  = "C:\\ts\\1001_Nacht_-_Der_Ruhelose_(1~3).ts"
    nach = "E:\\Filme\\schnitt\\1001_Nacht_-_Der_Ruhelose_(1~3).mkv"

    cmd = ff.ffXcodeCmd(von, nach)

    print("Eingabe   : {0}".format(von))
    print("Ausgabe   : {0}".format(nach))
    print("----------------------------------------------------------------------")
    print("cmd       : {0}".format(cmd))
    print("Ende")
