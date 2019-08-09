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
        
        voltages=self.getVoltageRegions()
        keithleyCompliance=float(self.options['kcomp'])
        agilentCompliance=float(self.options['acomp'])
        if not self.debugMode:
            self.setCurrentMode(agilentCompliance)

        for volt in voltages:
            print("Currently at volt",volt)
            currents=self.getAllChannels(volt) #a dict
            list_currents=[c[1] for c in currents.items()]
            keithleyCurrent=-self.readKeithley()
            self.emit(volt,keithleyCurrent,'keithley',refresh=True)
            breached=self.softwareCompliance(list_currents,agilentCompliance)
            print("%.01f%% of pixels have reached compliance at %.02e"%(breached*100,agilentCompliance))
            if breached > 0.8:
                print("More than 80% of pixels have reached compliance!")
                break
            if self.forceStop:
                print("Force quitting")
                break
        self.powerDownKeithley()
        self.log.emit("Finished data taking.")
        self.done.emit('done')
        self.quit()

    def getAllChannels(self,volt):
        #Hard coding 26 channels here!
        self.setVoltage(volt)
        values={}
        for group in range(7):
            smu2,smu1,smu3,smu4=reverse_channel_map[group]
            if not self.debugMode: self.controller.setGroup(group)
            self.log.emit("Selecting group %d"%(group))
            if self.useDelays: time.sleep(self.delayBetweenGroups)
            currents=self.getAgilentValues() #Array of 4
            print(currents)
            for value,chan in zip(currents,[smu1,smu2,smu3,smu4]):
                if chan==99: continue
                values[chan]=value
                if chan == 26:
                    self.emit(volt,value,'guardRing',refresh=True)
                else:
                    self.emit(volt,value,str(chan),refresh=True)
        return values
