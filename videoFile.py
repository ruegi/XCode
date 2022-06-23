'''
Klassendefinition der Klasse videoFile
rg, 2021-07-30
'''
import os
from pymediainfo import MediaInfo

class videoFile:
    def __init__(self, fullPathName):        
        self.fullPathName = fullPathName
        _, tail = os.path.split(fullPathName)
        fname, fext = os.path.splitext(tail)
        self.name = fname
        self.ext = fext[1:]     # den Punkt übergehen        self.duration = 0   # FilmLänge in ms
        self.frameCount = 0
        self.fps = 0.0
        self.bitRate = 0
        self.weite = "1280"
        self.hoehe = "768"
        self.typ = "HD"
        self.duration = 0.0
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