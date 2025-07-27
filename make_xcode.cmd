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
@REM --include-data-files=d:\DEV\Py\XCode\.venv\Lib\site-packages\pymediainfo\MediaInfo.dll=.\ ^
@REM --standalone ^
@REM --include-data-files=./ffcmd.ini=./ ^
python -m nuitka^
    --windows-console-mode=disable^
    --enable-plugin=pyside6^
    --follow-imports^
    --output-dir=.\dist^
    --remove-output^
    --windows-icon-from-ico=./XC_1.ico^
    --standalone^
    xcode.py

echo Env kopieren...
copy .\.env.xcode.* .\dist\xcode.dist

echo ffcmd.ini kopieren...
copy .\ffcmd.ini .\dist\xcode.dist


:Ende
echo Ende aus Maus!

:Ende1
@rem jetzt ist aber Schluss
