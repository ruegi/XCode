@echo off
echo Achtung!
echo 1. XCODE2 ist veraltet (das wart ein Experiment mit n parallelen TransCodes...)
echo 2. Die App xcode wird jetzt mit NUITKA gebaut
echo    Bitte dafür 'nuit.cmd' aufrufen!
echo -----------------------------------------
goto Ende

rem pyuic5 -x XCodeUI2.ui -o XCodeUI2.py
rem pyuic5 -x transcodeWinUI.ui -o transcodeWinUI.py
rem make Datei für XCode2; das ist das aktuelle XCode Tool
rem rg 2023-03-08
rem
rem VERALTET!!!
rem Benutze statt dessen xcode.py und xcodeUI.py
echo VERALTET! Do not use any more!
goto Ende

pyuic6 -x XCodeUI2.ui -o XCodeUI2.py
pyuic6 -x transcodeWinUI.ui -o transcodeWinUI.py

if "%1"=="full" goto Comp
goto Ende

:Comp
pyinstaller -w -i XC.ico --clean -y XCode2.py
copy .\XC.ico .\dist\XCode2
copy .\ffcmd.ini .\dist\XCode2

:Ende
echo Fertig!

