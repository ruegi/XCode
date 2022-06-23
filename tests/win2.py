from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout
from PyQt5.QtCore import pyqtSignal

import sys, time

from random import randint


class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    sender = pyqtSignal(int, name="sender")

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0,100))
        layout.addWidget(self.label)
        self.button = QPushButton('Sende Zahl!')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.senden)
        self.setWindowTitle('Second Window')
        self.setLayout(layout)
    
    def senden(self):
        # for i in range(10):
        i = randint(1,1111)
        txt = str(i)
        self.sender.emit(i)
        self.label.setText("Gesendet: " + txt)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.setWindowTitle('Main Window')
        layout = QGridLayout()

        self.label = QLabel()
        layout.addWidget(self.label)
        self.label.setText(" ")

        self.button = QPushButton('Switch Window')
        self.button.clicked.connect(self.show_new_window)
        layout.addWidget(self.button)
        wid.setLayout(layout)

        print(app.primaryScreen())

        d = app.desktop()

        print(d.screenGeometry())
        print(d.availableGeometry(), d.availableGeometry().width())
        print(d.availableGeometry(), d.availableGeometry().height())

        print(d.screenCount())            

    def receiver(self, zahl):
        self.label.setText("Empfangen: " + str(zahl))

    def show_new_window(self, checked):
        if self.w is None:
            self.w = AnotherWindow()
            self.w.sender.connect(self.receiver)
            self.w.show()
        else:
            self.w.sender.disconnect()
            self.w.close()
            self.w = None


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
