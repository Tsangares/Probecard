from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton,QApplication
from random import random
if __package__ in [None,""]:
    from utilities.controller_maps import Resistor
    from utilities import writeExcel,attachFile,send_mail
    from windows import IV_Window,DetailWindow
    from BasicDaqWindow import BasicDaqWindow
else:
    from .utilities.controller_maps import Resistor
    from .utilities import writeExcel,attachFile,send_mail
    from .windows import IV_Window,DetailWindow
    from .BasicDaqWindow import BasicDaqWindow
from time import sleep

class SinglePixelDaq(QThread):
    newPoint=pyqtSignal(float,float,str,bool)
    def run(self):
        print("Adding points")
        for i in range(20):
            for j in range(4):
                self.newPoint.emit(i,random(),str(j),True)
                sleep(.2)
        
if __name__=='__main__':
    #Make a test
    
    #Create basic GUI
    gui=QApplication(['test'])
    daq=BasicDaqWindow()
    gui.window=daq

    #Create a plotting thread
    test=TestPlotting()
    test.newPoint.connect(daq.addPoint)
    test.start()
    
    gui.exec_()
