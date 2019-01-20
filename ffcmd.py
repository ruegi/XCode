# -*- coding: utf-8 -*-
"""
Created on Sun, 2019-01-19

@author: rg

Name: ffcmd
laden der ffmpeg-Befehle aus einer Datei und montieren des Transcode-Aufrufs

"""

class ffmpegcmd:
    def __init__(self, lname=os.path.basename(__file__) + ".ini"):
        self.initFile = lname


def ffmpegBefehl(ts_von, ts_nach):
    # das "&" stört im Aufruf, es muss maskiert werden
    #        von = ts_von.replace("&", "^&")
    #        nach = ts_nach.replace("&", "^&")
    #        cmd = "cmd /C c:\\ffmpeg\\bin\\ffmpeg -i "
    cmd = "c:\\ffmpeg\\bin\\ffmpeg -i "
    cmd = cmd + "\"{0}\" ".format(ts_von)
    # cmd = cmd + ' -map 0:v -map 0:a:0 -c:v h264_nvenc -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska '
    # cmd = cmd + '-c:v h264_nvenc -c:a copy -c:s copy -b:v 1200K -maxrate 1400K -bufsize:v 4000k -bf 2 -g 150 -i_qfactor 1.1 -b_qfactor 1.25 -qmin 1 -qmax 50 -f matroska -y '
    # die folgenden Parameter haben die Eigenschaften (2018-12-13):
    #  - gute Videoqualität per nvenc;
    #  - alle Audios werden kopiert
    #  - Deutscher Untertitel wirde als dvdsub einkopiert
    cmd = cmd + '-map 0 -c:v h264_nvenc -c:a copy -c:s dvdsub  -profile:v main -preset fast -f matroska -y '
    cmd = cmd + "\"{0}\"".format(ts_nach)
    return cmd