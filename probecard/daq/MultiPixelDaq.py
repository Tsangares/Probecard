from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton,QApplication
from random import random

#Imports are lengthy because linking files is different when its a pip package.
if __package__ in [None,""]:
    from utilities import writeExcel,attachFile,send_mail
    from windows import IV_Window,DetailWindow
    from BaseProbecardThread import BaseProbecardThread
    from BasicDaqWindow import BasicDaqWindow
else:
    from .utilities import writeExcel,attachFile,send_mail
    from .windows import IV_Window,DetailWindow
    from .BaseProbecardThread import BaseProbecardThread
    from .BasicDaqWindow import BasicDaqWindow
    from time import sleep

class MultiPixelDaq(BaseProbecardThread):
    def run(self):
        super(SinglePixelDaq,self).run()
        if self.debugMode:
            print("In debug mode!")
        voltages=self.getVoltageRegions()
        keithleyCompliance=float(self.options['kcomp'])
        agilentCompliance=float(self.options['acomp'])
        for volt in voltages:
            print("Currently at volt",volt)
            if self.softwareCompliance(keithleyCurrent,keithleyCompliance) > 0.8:
                print("80% of pixels have reached compliance!")
                break
        if not self.debugMode:
            self.keithley.powerDownPSU()
        self.log.emit("Finished data taking.")
        self.done.emit('done')
        self.quit()
