#  python3
# -*- coding: utf_8 -*
#
# logger.py
# ----------------
# Exportiert die Prozeduren
#
#
#
#
#  rg, ab 2016-08-23
#
# Änderungen
# ab 2016-10-26 objektorientiert
# 2016-10-27    vereinfachtes Handling; TimeStamp eingeführt
# 2021-11-23    bessere Ausrichtung bei Mutli-Line Texten & TimeStamp
# -----------------------------------------------------------------------------------
from datetime import datetime
import os

class logFile:

    def __init__(self, lname=os.path.basename(__file__)+".log", TimeStamp=None, printout=True):
        self.TimeStamp = False
        self.LogName = lname
        self.printout = printout
        _zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        _wid = 109 if TimeStamp == True else 80
        self.logEintrag("{0} : Beginn LOG [{1}]".format(_zeit, self.LogName))
        # self.logEintrag(("Beginn LOG [{0}] um {1}\n" + _wid * "-").format(self.LogName, _zeit))
        if TimeStamp == True:
            self.TimeStamp = True

    def close(self) -> object:
        _zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        _wid = 109 if self.TimeStamp else 80
        self.TimeStamp = False  # nötig, um den doppelten Timestamp zu verhindern
        self.logEintrag("{0} : Ende  LOG [{0}]".format(_zeit, self.LogName))
        # self.logEintrag(_wid * "-" + "\n>>Ende LOG [{0}] um {1}\n\n".format(self.LogName, _zeit))

    def log(self, logText):
        self.logEintrag(logText)

    def logEintrag(self, logText):
        """
        schreibt den String logText in die Log-Datei und ggf. auf den Schirm
        :rtype: nil
        :param lstr: string
        :return: nil
        """
        
        # lts = logText.split(os.linesep)
        lts = logText.split("\n")
        dtme = datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " : "
        dtme_blank = " " * len(dtme)
        first = True
        # akku = ""
        lg = open(self.LogName, encoding="utf-8", mode='a')            
        for st in lts:
            if self.TimeStamp:
                if first:
                    lt = dtme + st
                    first = False
                else:
                    lt = dtme_blank + st
            else:
                lt = st
            # akku += lt + "\n"            
            print(lt, file=lg, end="\n")
            if self.printout:
                print(lt)
            # 
        # print(akku, file=lg, end="\n")
        # lg.write(akku + "\n")
        lg.close()

# ----Klasse LogFile Ende----------------------------------------------------------------------


def openlog(logName, TimeStamp=False, printout=True):
    """
    Eröffnet das Logging, indem eine Instanz eines Log-Objekts erzeugt
    und zurückgegeben wird.
    :param logName: Name der LogDatei (obligatorisch)
            TimeStamp: boolean  (optional; default = False)
                        bestimmt, ob jede Zeile zu beginn einen Zeitstempel enhält
        :return Referenz auf ein Log-Objekt
    """
    return(logFile(logName, TimeStamp, printout))

if __name__ == "__main__":
    log = openlog(os.path.basename(__file__)+".log", TimeStamp=True)
    log.logEintrag("Erster!")
    log.log("Letzter Log-Eintrag")
    log.log("Mehrzeiler!\nDas ist die 2. Zeile.\nUnd das ist der Schluss.\n")
    log.log("Bye!")
    log.close()


