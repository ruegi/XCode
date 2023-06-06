# -*- coding: utf-8 -*-
"""
Created on 2018-05-19

@author: rg

Liste.py
Verwaltet eine simple lineare Liste von Objekten
Letzte Änderungen:
2021-02-22      findPos und findAll ergänzt
2021-11-21      getRow ergänzt

verfügbare Attribute:
    size        Umfang der Liste; eine leere Liste hat size = 0
    lastPos     letzte (oder aktuell) abgefragte Position 0 .. (size -1); 
				lastPos = -1 bei einer neuen Liste, die noch nicht durchlaufen wurde
    lastObj     aktuelles oder zuletzt abgefragtes Objekt ; lastObj = None sonst

verfügbare Methoden:
    append(Objekt)              fügt ein Objekt der Liste hinzu

    findFirst()                 liefert das erste Objekt der Liste aus; None bei einer leeren Liste
    findLast()                  liefert das letzte Objekt der Liste aus; None bei einer leeren Liste
    findNext()                  liefert ausgehend von lastPos das nächste Objekt aus;
                                    ist die Liste leer oder das Ende erreicht, wird None zurückgeliefert
					                ist die Liste noch nicht abgefragt worden, wird das erste Element zurückgeliefert
    findPrev()                  liefert ausgehend von lastPos das vorhergehende Objekt aus;
                                    ist die Liste leer oder der Anfang erreicht, wird None zurückgeliefert
    findPos(pos)                Positioniert auf den Eintrag mit Position 'pos'. pos muss zwischen 0 und size-1 sein

    isLast()                    gibt True zurück, wenn das letzte Element gefunden wurde, sonst False
    isFirst()                   gibt True zurück, wenn das erste Element gefunden wurde, sonst False

    find(AttributName, Wert)    sucht den Wert eines Attributs eines Objekts; Wenn in der Liste simple Typen gespeichert sind,
                                    wird als Attribut "" oder None angegeben
                                    Die Liste steht anschlißend auf dem 1. Satz
    findAll("Attribut", "Wert") Liefert eine Liste der Indizes aller Sätze, die im Attribut den Wert stehen haben
                                    Die Liste steht anschlißend auf dem 1. Satz

    zap()                       Löscht die enthaltene Liste und setzt alle Verwaltungsvariablen zurück
"""


class liste():
    def __init__(self):
        self.liste = []
        self.size = 0
        self.lastPos = -1
        self.lastObj = None

    def append(self, eintrag):
        self.liste.append(eintrag)
        self.size += 1

    def findFirst(self):
        if self.size > 0:
            self.lastPos = 0
            self.lastObj = self.liste[self.lastPos]
            return self.lastObj
        else:
            return None

    def findLast(self):
        if self.size > 0:
            self.lastPos = self.size - 1
            self.lastObj = self.liste[self.lastPos]
            return self.lastObj
        else:
            return None

    def findNext(self):
        if self.size > 0:
            if self.lastPos == self.size - 1:  		# Ende erreicht; lastPos bleibt auf size-1
                self.lastObj = None
            # elif self.lastPos == - 1:				# Anfang; erstes Element ausliefern
            #     self.lastPos = 0
            #     self.lastObj = self.liste[self.lastPos]
            #
            else:									# das nächste Element ausliefern
                self.lastPos += 1
                self.lastObj = self.liste[self.lastPos]
            return self.lastObj
        else:
            return None

    def findPrev(self):
        if self.size > 0:
            # Anfang erreicht
            if self.lastPos == 0:
                self.lastPos = -1
                self.lastObj = None
                return self.lastObj
            else:
                self.lastPos -= 1
                self.lastObj = self.liste[self.lastPos]
                return self.lastObj
        else:
            return None

    def isNew(self):
        if self.size > 0 and self.lastPos == -1:
            return True
        else:
            return False

    def isFirst(self):
        if self.lastPos == 0:
            return True
        else:
            return False

    def isLast(self):
        if self.size > 0:
            if self.lastPos == self.size - 1:
                return True
        return False

    def find(self, attribut, wert):
        '''
        sucht in der Liste nach dem Attribut & Wert (lineare Suche)
        wird der Wert gefunden, wird das Objekt der Liste zurückgegeben
        sonst wird None zurückgegeben
        '''
        # erst den Typ der Objekte bestimmen
        d = self.findFirst()
        if type(d).__name__ in ("int", "long", "float", "str"):
            otyp = False
        else:
            otyp = True
        # print(otyp, "!!!!!!", type(d).__name__)
        for i in range(self.size):
            d = self.liste[i]
            # print("v =", v)
            if otyp:    # In der Liste stehen Objekte
                v = vars(d)
                if attribut in v:
                    if v[attribut] == wert:
                        return self.liste[i]    # Treffer
                else:
                    return None  # Attribut gibts nicht
            else:   # simple Typen in der Liste
                if d == wert:
                    return d

        return None  # nichts gefunden

    def findPos(self, pos: int):
        # positioniert auf Satz Nr. pos, wenn möglich, sonst none
        if (pos > -1) and (pos < self.size):
            self.lastpos = pos
            self.lastObj = self.liste[pos]
            return self.liste[pos]
        else:
            return None

    def findAll(self, attribut, wert):
        # findet alle Sätze, deren Attribut den angegebenen Wert haben
        # und gibt die Liste der Satznummern zurück

        erglst = []

        # erst den Typ der Objekte bestimmen
        d = self.findFirst()
        if type(d).__name__ in ("int", "long", "float", "str"):
            otyp = False
            if not type(d) == type(wert):
                return None
        else:
            otyp = True
            v = vars(d)
            if not attribut in v:
                return None

        if otyp:
            for i in range(self.size):
                v = vars(self.liste[i])
                if v[attribut] == wert:
                    erglst.append(i)    # Treffer
        else:   # simple Typen in der Liste
            for i in range(self.size):
                if d == wert:
                    erglst.append(i)    # Treffer
        return erglst

    def zap(self):
        # löscht die Liste und alle Verwaltungsvariablen
        #
        self.liste = []
        self.size = 0
        self.lastPos = -1
        self.lastObj = None

    def getRow(self, row):
        if row < self.size:
            return self.liste[row]
        else:
            return None


if __name__ == '__main__':
    class Beispiel():
        def __init__(self, Name, Vorname, Alter):
            self.Name = Name
            self.Vorname = Vorname
            self.Alter = Alter

        def __str__(self):
            return "Name: " + self.Vorname + " " + self.Name + "; Alter: " + str(self.Alter)

    l = liste()
    a = Beispiel("Meier", "Peter", 24)
    b = Beispiel("Hamadi", "Allo", 14)
    c = Beispiel("Timpte", "Thea", 84)

    for e in [a, b, c]:
        l.append(e)

    neul = liste()
    for e in [123, 345, 567]:
        neul.append(e)

    print("Liste l hat {} Einträge!".format(l.size))

    # l.findFirst()

    print("Is New? - {}".format(l.isNew()))

    while not (l.findNext() is None):
        print("Liste l hat den Eintrag: {} !".format(l.lastObj))

    print("Ende der Liste!")

    print("Is New? - {}".format(l.isNew()))

    print("Erster Eintrag: {}".format(l.findFirst()))
    print("Is First? - {}".format(l.isFirst()))
    print("Is New? - {}".format(l.isNew()))
    print("Letzter Eintrag: {}".format(l.findLast()))
    print("Is Last? - {}".format(l.isLast()))
    print("Is New? - {}".format(l.isNew()))
    print("VorLetzter Eintrag: {}".format(l.findPrev()))
    print("Is First? - {} / Is Last? - {} / Is New? - {}".format(l.isFirst(),
          l.isLast(), l.isNew()))

    print("-"*20)

    o = l.find("Vorname", "Thea")
    if o is None:
        print("Find Thea? {}", "Nixgefunden!")
    else:
        print("Find Thea? {}".format(o))

    print("-"*20)
    # print(type(1.0).__name__, type("a").__name__, type(a).__name__)

    # test einer Liste mit int-Objekten
    x = neul.find(None, 345)
    print("In neuL gefunden! {}".format(x))

    print("Eintrag 1: {}".format(l.getRow(1)))
    print("Eintrag 0: {}".format(l.getRow(0)))

    print("OK")
