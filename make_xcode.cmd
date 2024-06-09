@echo off
echo Achtung!
echo Die App 'xcode' wird jetzt mit NUITKA gebaut
echo -----------------------------------------
echo XCodeUI.py erzeugen...
pyside6-uic XCodeUI.ui -o XCodeUI.py
if errorlevel 1 goto UIC-FEHLER
echo OK
goto NEXT

:UIC-FEHLER
echo FEHLER beim Aufruf von pyside6-UIC !
echo Ende mit Fehler!
goto Ende1

:NEXT
if "%1"=="full" goto EXE
goto Ende

:EXE
python -m nuitka --standalone ^
    --windows-disable-console ^
    --enable-plugin=pyside6 ^
    --include-data-files=d:\DEV\Py\XCode\.venv\Lib\site-packages\pymediainfo\MediaInfo.dll=.\ ^
    --include-data-files=d:\DEV\Py\XCode\ffcmd.ini=.\ ^
    --output-dir=.\dist ^
    --remove-output ^
    --windows-icon-from-ico=.\XC_1.ico ^
    xcode.py

:Ende
echo Ende aus Maus!

:Ende1
rem jetzt ist aber Schluss

