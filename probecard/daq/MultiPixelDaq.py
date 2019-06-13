from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton,QApplication
from random import random
from time import sleep
    
#Imports are lengthy because linking files is different when its a pip package.
if __package__ in [None,""]:
    from utilities import writeExcel,attachFile,send_mail,reverse_channel_map
    from windows import IV_Window,DetailWindow
    from BaseProbecardThread import BaseProbecardThread
    from BasicDaqWindow import BasicDaqWindow
else:
    from .utilities import writeExcel,attachFile,send_mail,reverse_channel_map
    from .windows import IV_Window,DetailWindow
    from .BaseProbecardThread import BaseProbecardThread
    from .BasicDaqWindow import BasicDaqWindow


class MultiPixelDaq(BaseProbecardThread):
    useDelays=False
    delayBetweenGroups=.5

    def run(self):
        super(MultiPixelDaq,self).run()
        if self.debugMode:
            print("In debug mode!")
        voltages=self.getVoltageRegions()
        keithleyCompliance=float(self.options['kcomp'])
        agilentCompliance=float(self.options['acomp'])
        for volt in voltages:
            print("Currently at volt",volt)
            currents=self.getAllChannels() #a dict
            print(currents)
            keithleyCurrent=self.readKeithley()
            breached=self.softwareCompliance(currents,agilentCompliance)
            if self.softwareCompliance(currents,agilentCompliance) > 0.8:
                print("More than 80% of pixels have reached compliance!")
                break
            for chan,current in currents.items():
                print(chan,current)
                if current is None: continue
                self.emit(volt,current,str(chan),refresh=False)
            self.emit(volt,keithleyCurrent,'keithley',refresh=True)
        if not self.debugMode:
            self.keithley.powerDownPSU()
        self.log.emit("Finished data taking.")
        self.done.emit('done')
        self.quit()

    def getAllChannels(self):
        #Hard coding 26 channels here!
        values={}
        for group in range(7):
            channelNumbers=list(reverse_channel_map[group])
            if not self.debugMode: self.controller.setGroup(i)
            self.log.emit("Selecting group %d with %s channels"%(group,channelNumbers))
            if self.useDelays: time.sleep(self.delayBetweenGroups)
            currents=self.getAgilentValues() #Array of 4
            for value,chan in zip(currents,channelNumbers):
                if chan==99: continue
                values[chan]=value
        return values
