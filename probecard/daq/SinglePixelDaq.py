from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton,QApplication
from random import random
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

'''
To implement a new daq:
 1) Inherit BaseProbecardThread to get many commonly used functions.
 2) Write a run function that will be the entry point to the thread
     In the run function call the super's run function first then
     implement your new startup configurations (like set the mode).
     All options from the menu are stored in self.options['key']
 3) Write an aquire function that is called after the run function.
     In your aquire function, specify your experiment/collect data.
 TODO: 4) Unwritten data finalization!
 Warning: The hardest part is implementing the voltage regions.
'''
class SinglePixelDaq(BaseProbecardThread):

    def run(self):
        super(SinglePixelDaq,self).run()
        self.controllerDelay=1
        if not self.debugMode:
            print("Setting controller to voltage mode.")
            self.setVoltageMode()
            sleep(self.controllerDelay)
            self.controller.setGain(1) #highest resistance
            print("Setting gain resistor to 1 or %sohms."%self.controller.getResistance())
            sleep(self.controllerDelay)
        channels=[int(chan) for chan in self.options['channel_number'].split(',') if chan != '']
        voltages=self.getVoltageRegions()

        compliance=float(self.options['kcomp'])
        for volt in voltages:
            keithleyCurrent,agilentCurrents=self.getValues(volt,channels)
            while agilentCurrents is None:
                print("failed gain check")
                keithleyCurrent,agilentCurrents=self.getValues(volt,channels)
                #This loop happens if the gain is wrong from checkGain()
            print("Agilent Current: ",agilentCurrents)
            print("Keithley Current:", keithleyCurrent)
            for chan,current in zip(channels,agilentCurrents):
                self.emit(volt,current,str(chan),refresh=False)
            self.emit(volt,keithleyCurrent,'keithley',refresh=True)
            if self.softwareCompliance(keithleyCurrent,compliance) > 0.1:
                print("Software compliance breached!")
                break
            if self.forceStop:
                print("Force quitting")
                break
        self.powerDownKeithley()
        self.log.emit("Finished data taking.")
        self.done.emit('done')
        self.quit()
                

    def checkGain(self,voltage):
        if voltage > 14:
            print("Gain is too high, dropping",voltage)
            self.controller.dropGain()
            return False
        return True

    def getCurrents(self):
        values=self.readAgilent()
        print("Agilent raw",values)
        currents={}
        for channel,voltage in values.items():
            if not self.checkGain(voltage):
                return None
            if not self.debugMode:
                if int(channel[-1]) == 1:
                    print("Agilent Voltage: ",voltage)
                    print("Controller Resistance: ",self.controller.getResistance())
                currents['V%s'%channel[-1]] = voltage/self.controller.getResistance()
            else:
                currents['V%s'%channel[-1]] = voltage
        return currents['V1']
    
    def getValues(self,volt,channels):
        #Single Pixel
        self.setVoltage(volt)
        keithley=self.readKeithley()
        agilent=[]
        print(self.controller)
        for chan in channels:
            if not self.debugMode: self.controller.setChannel(chan)
            sleep(self.controllerDelay)
            current=self.getCurrents()
            if current is None: return None,None
            agilent.append(current)
        return -keithley,agilent
            
        
    
        
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
