pyuic5 -x XCodeUI.ui -o XCodeUI.py
pyuic5 -x transcodeWinUI.ui -o transcodeWinUI.py
rem pyinstaller -w -i XC.ico --clean -y XCode.py
rem copy .\XC.ico .\dist\XCode
rem copy .\ffcmd.ini .\dist\XCode
echo Fertig!

