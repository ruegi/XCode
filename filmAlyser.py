'''
analysiert das übergebene Video

'''
import os
import sys
import subprocess

class Konstanten:
    MEDIAINFO = r'c:\tools\MediaInfo\MediaInfo.exe'

def _runit(cmd):
    try:
        pobj = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    except:
        print("Unbekannter Fehler beim run-Aufruf!")
        print("Unexpected error:{0}".format(sys.exc_info()[0]))

    return pobj

def get_encoding(filmname, Test=False):

    codec = "Unbekannt"
    weite = "0"
    hoehe = "0"
    Bitrate = "0"
    FCount = "0"

    cmd = Konstanten.MEDIAINFO + ' --Inform="Video;Resolution %Width% %Height%\\r\\nCodec %Format% %Format_Version%\\r\\nBitrate %BitRate%\\r\\nFrameCount %FrameCount%" ' + '"' + filmname + '"'
    if Test:
        print(cmd)
    pobj = _runit(cmd)
    if pobj.returncode == 0:
        ausg = pobj.stdout
        if Test:
              print(ausg)
        buf = ausg.split("\n")
        for line in buf:
            mots = line.strip().split(" ")
            if mots[0] == "Resolution":
                # line.startswith("Resolution"):                
                weite = mots[1]
                hoehe = mots[2]
            elif mots[0] == "Codec":
                codec = mots[1]
                if len(mots) == 3:
                    codec += mots[3]
            elif mots[0] == "Bitrate":
                if len(mots) > 1:
                    Bitrate = mots[1]
            elif mots[0] == "FrameCount":
                if len(mots) > 1:
                    FCount = mots[1]
    else:
        if Test:
            print(pobj.returncode)

    return  codec, weite, hoehe, Bitrate, FCount


# def get_encoding(filmname, Test=False):
#     cmd = r'C:\ffmpeg\\bin\ffprobe -hide_banner -show_streams -select_streams v "' + filmname + '"'
#     if Test:
#         print(cmd)
#     pobj = _runit(cmd)
#     if pobj.returncode == 0:
#         # filausgabe analysieren
#         ausg = pobj.stderr
#         # print(ausg)
#         buf = ausg.split("\n")
#         for line in buf:
#             line = line.strip()            
#             # auf die passende Zeile durchblättern
#             if line.startswith('Stream #0:'):
#                 felder = line.split(" ")
#                 if felder[2] == "Video:":
#                     # i = 0
#                     # for f in felder:
#                     #     print(f"({i}) {f}")
#                     #     i+=1
#                     # print(f"Der gesuchte Parameter ist: ({felder[3]})")
#                     codec = felder[3]
#                     if codec == "h264":
#                         return "h264"
#                     elif codec == "mpeg2video":
#                         return "mpg"
#                     elif codec == "hevc":
#                         return "hevc"
#                     else:
#                         return "not known : " + codec                
#     else:
#         print(f'Fehler {pobj.returncode}')
#         print(f'{pobj.stderr}')
#         return None

if __name__ == "__main__":        
    # codec, weite, hoehe, bitrate, FCount = get_encoding(r'C:\ts\1001_Nacht_-_Der_Ruhelose_(1~3).ts', Test=True)
    
    # print("Test:", codec, weite, hoehe, bitrate, FCount)
    
    # print ("-"*40)

    codec, weite, hoehe, bitrate, FCount = get_encoding(r'C:\ts\1001_Nacht_(2~3)_Der_Verzweifelte.ts', Test=True)
    
    print("Test:", codec, weite, hoehe, bitrate, FCount)

    print ("-"*40)

    codec, weite, hoehe, bitrate, FCount = get_encoding(r'C:\ts\KonoSuba.ts', Test=True)
    
    print("Test:", codec, weite, hoehe, bitrate, FCount)

