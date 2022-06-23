pyuic5 -x XCodeUI2.ui -o XCodeUI2.py
pyuic5 -x transcodeWinUI.ui -o transcodeWinUI.py
pyinstaller -w -i XC.ico --clean -y XCode2.py
copy .\XC.ico .\dist\XCode2
copy .\ffcmd.ini .\dist\XCode2
echo Fertig!

