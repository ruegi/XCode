pyuic5 -x XCodeUI.ui -o XCodeUI.py
pyinstaller -w -i XC.ico --clean -y XCode.py
copy .\XC.ico .\dist\XCode
copy .\ffcmd.ini .\dist\XCode
echo Fertig!
pause
