'''
videoDetails.py
    Diese Funktion gibt die wichtigsten Video-Details zurück.
    Enthalten sind:
    - getVideoSpecs(videoname: str) -> dict

Versionen:
    1.0.0 - 2025-04-17
        - erste eigenständige Version

'''
# coding: utf-8

import subprocess

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

    # print("pobj.stdout: ", pobj.stdout)

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
        try:
            dur = float(details["duration"])
        except ValueError:
            dur = None
        erg["duration"] = dur
    else:
        erg["duration"] = None

    if "DURATION" in details:
        wert = details["DURATION"]
        if "\\" in wert:
            werte = wert.split("\\:")
        elif ":" in wert:
            werte = wert.split(":")
        else:
            werte = [wert]
        if len(werte) == 3:
            wert = int(werte[0])*3600 + int(werte[1])*60 + float(werte[2])
        else:
           wert = float(werte[0])
        erg["duration"] = wert

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

    if not "nb_frames" in details or details["nb_frames"] == "N/A":
        if "fps" in erg and "duration" in erg:
            erg["frameCnt"] = int(erg["duration"] * erg["fps"])
        else:
            erg["frameCnt"] = None
    else:
        erg["frameCnt"] = int(details["nb_frames"])



    # gib das Ergebnis zurück
    return erg

if __name__ == "__main__":
    # Beispielaufruf
    # video_name = "/home/ruegi/Videos/schnitt/Central_Intelligence_(2016).mkv"
    # video_name = "/home/ruegi/Videos/schnitt/Adiós_Buenos_Aires.mkv"
    video_name = "/home/ruegi/Videos/ts/Fitting_In_(2023).ts"
    specs = getVideoSpecs(video_name)
    if specs:
        print("Video-Spezifikationen:")
        for key, value in specs.items():
            print(f"{key}: {value}")
    else:
        print("Fehler beim Abrufen der Video-Spezifikationen.")
