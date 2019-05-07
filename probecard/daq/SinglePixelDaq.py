from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton
from .utilities.controller_maps import Resistor
from .utilities import writeExcel,attachFile,send_mail
from .windows import IV_Window

if __name__=='__main__':
    print("Single Pixel Daq")
