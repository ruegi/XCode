# XCode
Transcodiert eine Liste von ts-Files (Filme) mittels ffmpeg.
Die ffmpeg Parameter wurden durch eifriges testen und mit viel Hilfe aus dem Netz ermttelt.

(Hilfsmittel dazu waren ab-av1 und ffmpeg, mit denen ich testweise kodieren und den jeweiligen vmaf bestimmen konnte. 
Für mich war ein Mindestwert von 94% notwendig für eine erlogreiche Konvertierung)

XCode liest eine Liste von *.ts (*.mpeg etc) Files ein und transcodiert sie nach drücken von "Start" in einen ZielOrdner transkodiert abgelegt.
Die GUI war ursprünglch ein PyQT5 Projekt, jetzt ist es nach PyQt6 gewechselt.
Es schreibt dabei eine Logdatei und zeigt den Fortschritt in einem GUI Fenster an.

XCode nutzt zum transcodieren die Progamm-Suite von ffmpeg, die es in C:\ffmpeg erwartet.
Der Transcode wird durch die Ini-Datei "ffcmd.ini" gesteuert, allerdings wird dieser Befehl noch je nach Codierung des Quell-Films in ffmcd.py angepasst.
Einzelne Filme können per Doppelklick in der GUI für das transkodieren ab- und angeschaltet werden.

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

ruegi

