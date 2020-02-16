pyuic5 -x XCodeUI.ui -o XCdeUI.py
pyinstaller -w -i XC.ico --clean -y XCode_process_mitliste.py
copy .\XC.ico .\dist\XCode_process_mitliste
copy .\ffcmd.ini .\dist\XCode_process_mitliste
echo Fertig!
pause
