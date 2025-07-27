# XCode

Transcodiert eine Liste von ts-Files (Filme) mittels ffmpeg.

## Essentials

Als letztes benutztes Environment:  uv unter python 3.13.5
                                    (vorletztes war *poetry* mit python 3.12.7)
                                    (Kompiliert mittels *nuitka*)
                                    (Migriert von PyQt6 nach *PySide6*)
Zentrale App: *xcode.py*

(Die App xcode2.py war ein Versuch mit mehreren parallelen Transcodes mittels nvenc.
Das war ein Fehlschlag, weil jeder der n xcodes das n-fache seiner Zeit benötigte,
also gab es keinen Performance Gewinn.)

Die ffmpeg Parameter wurden durch eifriges Testen und mit viel Hilfe aus dem Netz ermttelt.
(Hilfsmittel dazu waren ab-av1 und ffmpeg, mit denen ich testweise kodieren und den jeweiligen vmaf bestimmen konnte.
Für mich war ein VMAF Mindestwert von 94% für eine erfolgreiche Konvertierung notwendig.)

XCode liest eine Liste von *.ts (*.mpeg etc) Files ein und transcodiert sie nach drücken von "Start" in einen ZielOrdner.
Die GUI war ursprünglch ein PyQT5 Projekt, dann war es nach PyQt6 gewechselt. Zuletzt habe ich pySide6 eingespeannt.
Es schreibt dabei eine Logdatei und zeigt den Fortschritt in einem GUI Fenster an.

XCode nutzt zum transcodieren die Progamm-Suite von ffmpeg.
Der Transcode wird durch die Ini-Datei "ffcmd.ini" gesteuert, allerdings wird dieser Befehl noch je nach Codierung des Quell-Films in ffmcd.py angepasst.
Einzelne Filme können per Doppelklick in der GUI für das transkodieren ab- und angeschaltet werden.

Probleme:
p1: der Fortschritt wurde ursprünglich in jeder Zeile der BrowserTabelle in einem FortschrittsBalken angezeigt.
    Bei Neukompilierung funktionierte des unter PyQt6 nicht mehr. Eine ALternative hatte ich nicht gefunden, also habe ich nur eine Prozentzahl angezeigt.
    Lösung: Ich zeige nur noch die jeweiligen Prozentwerte in der Tabelle an

p2: Beim Kompilieren mittels pyInstaller wird jetzt stets ein VirenVerdacht ausgeworfen, das den Vorgang stoppt.
    Ursuche unklar.
    Lösung: Der Wechsel nach 'nuitka' löste das Problem

### Zur Historie

2021-04-10:
Das derzeitige Hauptprogramm ist XCode_process_mitliste.py, der in zukünftigen Versionen einfach nur XCode.py heißen wird.

2021-04-11:
Jetzt ist XCode.py das Hauptprogramm, XCode_process_mitliste.py ist überflüssig.

2021-11-24:
Neue Version XCode2.py.
Diese Version ist auf n simultane Transcodierungen eingerichtet. Funktioniert hat das bis n=3.
Bei n=4 scheitert die 4. Tanscodierung an einem "out of memory" Fehler.
Ernüchternd: die gleichzeitigen Transcodierungen teilen sich eine Grafikkarte.
Darum reduziert sich die Geschwindigkeit auf 1/n. Man hat also keinen Geschwindigkeitsvorteil.
Ich arbeite daher mit n = 1.

2022-03-11:
Umstellung auf PyQt6.
Neue Farbgebung von xcode2.py; der Fortschrittsbalken in der Tabelle der zu trankodierenden Filme wurde entfernt, da ich keine Möglichkeit fand, seine in meinem Kontext häßliche Farbe der "trunk" zu ändern.
Weitere Überarbeitung der Teilprogramme.
Der ExitStatus von ffmpeg wird nicht mehr beachtet, da er selbst bei einwandfrei bearbeiteten Videos von 0 verschieden ist, ohne dass ich eine Lösung / Bedeutung gefunden habe. (Die errors.h von ffmpeg half da auch nicht weiter.)
ffcmd.ini:
Die neuen Parameter {canvas_size} und {Untertitel} vermeiden einen Fehler, den das neue ffmpeg meldet.

2023-09-19:
Nach dem Wechsel nach AV1 Encoder waren enige Anpassungen vor allem im Auffangen der Fortschrtts-Meldungen nötg.
Dazu hatte ch festgestellt, dass es Konvertierungen von h265->AV1 gibt, die bei meinen Parametern die Filmdatei vergrößerten.
Wenn das festgestllt wird, wird die Konvertierung durh eine einfaches ffmpeg COPY ersetzt, das das Kontainerformat nur ändert und in der Regel kleiner als das Original ist. Das wird in der Log-Datei protokolliert.

2024-06-08
Migration von PyQt6 nach PySide6

2025-03:
<<<<<<< HEAD
Entfernen der Abhängigkeit von MediaInfo und danach von ffmpeg-python. Die Video Attribute werden statt dessen mittels openCV ausgelesen. Das ist erheblich verläßlicher in Bezug auf frameCount, um den Fortschritt zu formatieren.

2025-04:
Auch openCV macht erhebliche Probleme: zum Einen ist es absolut überdimensieniert, zum anderen kompiliert es nicht mit nuitka.
Die Lösung ist, einfach ffprobe direkt selber auszuwerten. Dabei kommt zu gute, dass man den oft nicht enthaltenen frameCount ungefähr selber aus avg_frame_rate und der duration selber ermittlen kann. Das reicht für die Fortshtittsanzeige aus.
Zudem wird XCode dadurch leichtgewichtiger.

ruegi. 2025-04-09
=======
Entfernen der Abhängigkeit von MediaInfo und danach von ffmpeg-python. Die Video Attribute werden statt dessen mittes openCV ausgelesen. Das ist erheblich verläßlicher in Bezug sug frameCount, um den Fortschritt zu formatieren.

ruegi. 2025-03-26
>>>>>>> cd27b41b63bcd5cde0c53b952b8be903ba6665a0
