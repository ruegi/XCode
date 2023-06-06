@echo off
rem pyuic5 -x XCodeUI2.ui -o XCodeUI2.py
rem pyuic5 -x transcodeWinUI.ui -o transcodeWinUI.py
rem make Datei für XCode; das ist das aktuelle XCode Tool
rem rg 2023-05-29
pyuic6 -x XCodeUI.ui -o XCodeUI.py
rem pyuic6 -x transcodeWinUI.ui -o transcodeWinUI.py

if "%1"=="full" goto EXE
goto Ende

:EXE
pyinstaller -w -i XC.ico --clean -y XCode.py
copy .\XC.ico .\dist\XCode
copy .\ffcmd.ini .\dist\XCode

:Ende
echo Fertig!

