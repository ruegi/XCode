pyuic5 -x XCodeUI.ui -o XCdeUI.py
pyinstaller -w -i XC.ico --clean XCode_process_mitliste.py
copy .\XC.ico .\dist\XCode_process_mitliste

echo Fertig!
pause
