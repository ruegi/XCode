'''
analysiert das übergebene Video

'''
import os
import sys
import subprocess

def _runit(cmd):
    try:
        pobj = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    except:
        print("Unbekannter Fehler beim run-Aufruf!")
        print("Unexpected error:{0}".format(sys.exc_info()[0]))

    return pobj

def get_encoding(filmname, Test=False):
    cmd = r'C:\ffmpeg\\bin\ffprobe -hide_banner -show_streams -select_streams v "' + filmname + '"'
    if Test:
        print(cmd)
    pobj = _runit(cmd)
    if pobj.returncode == 0:
        # filausgabe analysieren
        ausg = pobj.stderr
        # print(ausg)
        buf = ausg.split("\n")
        for line in buf:
            line = line.strip()            
            # auf die passende Zeile durchblättern
            if line.startswith('Stream #0:0'):
                felder = line.split(" ")                
                # i = 0
                # for f in felder:
                #     print(f"({i}) {f}")
                #     i+=1
                # print(f"Der gesuchte Parameter ist: ({felder[3]})")
                codec = felder[3]
                if codec == "h264":
                    return "h264"
                elif codec == "mpeg2video":
                    return "mpg"
                elif codec == "hevc":
                    return "hevc"
                else:
                    return "not known : " + codec
    else:
        print(f'Fehler {pobj.returncode}')
        print(f'{pobj.stderr}')
        return None

if __name__ == "__main__":
    # codec = get_encoding(r'C:\ts\Ame_+_Yuki_-_Die_Wolfskinder.ts')
    # get_encoding(r'C:\ts\Das_letzte_Problem.ts')
    codec = get_encoding(r'c:\ts\Blood_&_Treasure_-_Kleopatras_Fluch_(1-1)_Der_Agent_und_die_Meisterdiebin.ts', Test=False)
    print(codec)

