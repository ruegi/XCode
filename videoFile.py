"""
Klassendefinition der Klasse videoFile
rg, 2021-07-30
auf ffmpeg-python umgestellt ab 03.2025
"""

import os
import ffmpeg


class videoFile:
    def __init__(self, fullPathName):
        self.fullPathName = fullPathName
        _, tail = os.path.split(fullPathName)
        fname, fext = os.path.splitext(tail)
        self.name = fname
        self.ext = fext[1:]  # den Punkt übergehen        
        self.weite = "1280"
        self.hoehe = "800"
        self.g_track = None
        self.v_tracks = []
        self.a_tracks = []
        self.t_tracks = []
        self.duration = 0.0        
        self.weite = 0
        
        self.getVideoDetails()        
        self.typ = self.getVideoTyp()

    def getVideoDetails(self):
        try:
            probe = ffmpeg.probe(self.fullPathName)
            
            self.g_track = probe["format"]
            
            for track in probe['streams']:
                if track['codec_type'] == 'video':
                    self.v_tracks.append(track)
                elif track['codec_type'] == 'audio':
                    self.a_tracks.append(track)
                elif track['codec_type'] == 'subtitle':
                    self.t_tracks.append(track)
                else:
                    next
            if len(self.v_tracks) > 0:
                self.weite = self.v_tracks[0]["width"]
                self.hoehe = self.v_tracks[0]["height"]
        except ffmpeg.Error as err:
            print(f"Abbruch! (Fehler in ffmpeg.probe): {err}")
            return
    
    def getVideoTyp(self)-> str:
        breite = self.weite
        if breite < 1280:            
            return "SD"
        elif breite < 1920:
            return "HD"            
        elif breite < 3840:
            return "FullHD"
        else:
            return "4K"
            
