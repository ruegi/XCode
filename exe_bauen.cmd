pyuic5 -x XCodeUI.ui -o XCodeUI.py
pyinstaller -w -i XC.ico --clean -y -y -p D:\\DEV\\Py\\xcode\\xcode2 --hiddenimport transcodeWin --hiddenimport videoFile --hiddenimport sqlalchemy --hiddenimport pymediainfo --add-binary ./MediaInfo.dll;. -n XCode xcode2.py
copy .\XC.ico .\dist\XCode
copy 
copy .\ffcmd.ini .\dist\XCode
echo Fertig!

