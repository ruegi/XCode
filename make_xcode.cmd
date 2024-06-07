@echo off
echo Achtung!
echo Die App 'xcode' wird jetzt mit NUITKA gebaut
echo Bitte dafür 'nuit.cmd' aufrufen!
echo -----------------------------------------
goto Ende

rem pyuic5 -x XCodeUI2.ui -o XCodeUI2.py
rem pyuic5 -x transcodeWinUI.ui -o transcodeWinUI.py
rem make Datei für XCode; das ist das aktuelle XCode Tool
rem rg 2023-05-29
pyuic6 -x XCodeUI.ui -o XCodeUI.py
rem pyuic6 -x transcodeWinUI.ui -o transcodeWinUI.py

if "%1"=="full" goto EXE
goto Ende

:EXE
rem pyinstaller -w -i XC.ico --clean -y XCode.py
rem pyinstaller -w -i FLGGERM.ICO --clean -y XCode.py
pyinstaller --clean xcode.spec

rem if not exist .\dist\xcode goto Ende
if not exist .\dist\xcode\xcode.exe goto Ende
copy .\XC_1.ico .\dist\XCode
copy .\ffcmd.ini .\dist\XCode

:Ende
echo Fertig!

