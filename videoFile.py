'''
Klassendefinition der Klasse videoFile
rg, 2021-07-30
Änderungen
2023-05-30  rg      Parameter bitRate ergänzt 
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
        self.mInfo = None
        self.frameCount = 0
        self.fps = 0.0
        self.bitRate = 0
        self.weite = "1280"
        self.hoehe = "768"
        self.typ = "HD"
        self.duration = 0.0
        self.anzVideoTracks = 0
        self.anzAudioTracks = 0
        self.anzTextTracks = 0
        self.getVideoDetails()

    def getVideoDetails(self):
        try:
            media_info = MediaInfo.parse(self.fullPathName)
            self.mInfo = media_info
            g_track = media_info.general_tracks[0]
            v_track = media_info.video_tracks[0]            
            self.anzVideoTracks = len(media_info.video_tracks)
            self.anzAudioTracks = len(media_info.audio_tracks)
            self.anzTextTracks = len(media_info.text_tracks)
            v_fr = v_track.frame_rate
            v_fc = v_track.frame_count
            v_br = v_track.bitrate            
            g_du = g_track.duration
            self.fps = float(v_fr)
            self.weite = v_track.width
            iWeite  = int(self.weite)
            self.hoehe = v_track.height
            if not v_br:
                self.bitRate = g_track.overall_bit_rate
                # self.bitRate = str(v_track.bit_rate)
            if self.bitRate is None:
                self.bitRate = 0
            else:
                self.bitRate = str(int(self.bitRate / 1000)) + " kB/s"
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

if __name__ == '__main__': 
    vidf = "e:\\filme\\schnitt\\Quo_vadis_(1951).mkv"
    vid = videoFile(vidf)
    print("Video: ", vidf)
    print(f"Anzahl Video Tracks: {vid.anzVideoTracks}")    
    print(f"Anzahl Audio Tracks: {vid.anzAudioTracks}")    
    print(f"Anzahl Text Tracks: {vid.anzTextTracks}")    
    print("Video-Abmessungen: ", vid.weite, "x", vid.hoehe)
    print("Video-Anz.Frames: ", vid.frameCount)
    print("Video-fps: ", vid.fps)
    print("BitRate: ", vid.bitRate)
    
