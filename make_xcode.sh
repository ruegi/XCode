#!/bin/zsh
# -------------------------------------------------------------
source /home/ruegi/.cache/pypoetry/virtualenvs/xcode-tvfFPNOf-py3.12/bin/activate

echo "Achtung!"
echo "Die App 'xcode' wird mit NUITKA gebaut!"
# ------------------------------------------
# XCodeUI.py erzeugen...
PARMFULL="$1"
echo "PARMFULL=${PARMFULL}"
echo "Step 1"
pyside6-uic "XCodeUI.ui" -o "XCodeUI.py"
if (( $? ))
then
    echo "FEHLER beim Aufruf von pyside6-UIC !"
    echo "Ende mit Fehler!"
    # exit 3
else
    echo "Das UI [XCodeUI.ui] wurde neu übersetzt!"
    ls -la XCodeUI.py
fi

echo "Step 2"
if [[ "${PARMFULL}"=="full" ]]
then
    echo "Kompiliere jetzt..."
    python -m nuitka \
        --follow-imports \
        --plugin-enable=pyside6 \
        --windows-disable-console \
        --enable-plugin=pyside6 \
        --output-dir=./dist/xcode \
        --remove-output \
        --windows-icon-from-ico=./XC_1.ico \
        ./XCode.py
    cp ./ffcmd.ini ./dist/xcode
    cp ./.env.xcode ./dist/xcode
    cp ./XC_1.ico ./dist/xcode
else
    echo "ok"
fi

# Ende
echo "Ende aus Maus!"
exit 0
