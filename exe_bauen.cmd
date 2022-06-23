pyuic5 -x XCodeUI.ui -o XCodeUI.py
pyinstaller -w -i XC.ico --clean -y -y -p D:\\DEV\\Py\\xcode\\xcode2 --hiddenimport transcodeWin --hiddenimport sqlalchemy -n xcode xcode2.py
copy .\XC.ico .\dist\XCode
copy .\ffcmd.ini .\dist\XCode
echo Fertig!
pause
