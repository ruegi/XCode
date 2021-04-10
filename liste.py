# -*- coding: utf-8 -*-
"""
Created on 2018-05-19

@author: rg

Liste.py
Verwaltet eine simple lineare Liste von Objekten

verfügbare Attribute:
    size        Umfang der Liste; eine leere Liste hat size = -1
    lastPos     letzte (oder aktuell) abgefragte Position 0 .. (size -1)
    lastObj     aktuelles abgefragtes Objekt ; lastObj = None sonst

verfügbare Methoden:
    append(Objekt)  fügt ein Objekt der Liste hinzu
    findFirst()     liefert das erste Objekt der Liste aus; None bei einer leeren Liste
    findLast()      liefert das letzte Objekt der Liste aus; None bei einer leeren Liste
    findNext()      liefert ausgehend von lastPos das nächst Objekt aus;
                    ist die Liste leer oder das Ende erreicht, wird None zurückgeliefert
    findPrev()      liefert ausgehend von lastPos das vorhergehende Objekt aus;
                    ist die Liste leer oder der Anfang erreicht, wird None zurückgeliefert
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
            # Ende erreicht
            if self.lastPos == self.size - 1:
                self.lastPos = -1
                self.lastObj = None
                return self.lastObj
            else:
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
    
    def findRow(self, row):
        if row < self.size:
            return self.liste[row]
        else:
            return None
            

if __name__ == '__main__': 
    l = liste()
    for e in ["123", "234", "345"]:
        l.append(e)
        
    print("Liste l hat {} Einträge!".format(l.size))
    l.findFirst()
    
    while True:
        print("Liste l hat den Eintrag: {} !".format(l.lastObj))
        if l.findNext() is None:
            break
        
    print("Ende der Liste!")

    print("Erster Eintrag: {}".format(l.findFirst()))
    print("Letzter Eintrag: {}".format(l.findLast()))
    print("VorLetzter Eintrag: {}".format(l.findPrev()))
    print("OK")
        
    
    