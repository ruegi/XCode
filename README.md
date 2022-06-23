# XCode
Transcodiert eine Liste von ts-Files (Filme) mittels ffmpeg

XCode liest eine Liste von *.ts (*.mpeg etc) Files ein und transcodiert sie nach "Start" in einen ZielOrdner.
Die GUI ist ein PyQT5 Projekt.
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

ruegi

