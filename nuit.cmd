@echo off
rem make Datei für XCode; das ist das aktuelle XCode Tool
rem rg 2024-06-09
pyside6-uic XCodeUI.ui -o XCodeUI.py
rem pyuic6 -x transcodeWinUI.ui -o transcodeWinUI.py

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
    --windows-icon-from-ico=.\XC_1.ico^
    xcode.py


rem if not exist .\dist\xcode.dist\xcode.exe goto Ende
rem copy .\XC_1.ico .\dist\XCode.dist
echo .
rem echo Kopiere 'ffcmd.ini' nach .\dist\XCode.dist ...
rem copy .\ffcmd.ini .\dist\XCode.dist

:Ende
echo Fertig!

