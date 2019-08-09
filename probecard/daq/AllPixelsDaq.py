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

class AllPixelsDaq(BaseProbecardThread):
    def __init__(self,options):
        super(AllPixelsDaq,self).__init__(options,enableAgilent=False)

    def run(self):
        #Call the run function in BaseProbard Thread
        super(AllPixelsDaq,self).run()

        #Example of how to use debug mode
        if self.debugMode:
            print("In debug mode!")
        if not self.debugMode:
            print("Setting controller to ground mode.")
            controllerDelay=1
            self.controller.setGroundMode()
            sleep(controllerDelay)
            #self.controller.setGain(1) #highest resistance
            #print("Setting gain resistor to 1 or %sohms."%self.controller.getResistance())
            #sleep(controllerDelay)

        #Get an array of voltages based on the regions section of the menu screen.
        voltages=self.getVoltageRegions()

        #Get the keithley compliacne from the menu options
        #Note: All menu options are of type string
        compliance=float(self.options['kcomp'])

        #This is how you loop through each voltage step
        for volt in voltages:
            print("Now at volt",volt)
            keithleyCurrent=self.getValues(volt)
            print("Keithley Current:", keithleyCurrent)
            self.emit(volt,keithleyCurrent,'keithley',refresh=True)
            
            #Must account for the softwareCompliace!
            if self.softwareCompliance(keithleyCurrent,compliance) > 0.8:
                print("At least 80% of pixels have reached compliance!")
                break
            if self.forceStop:
                print("Force quitting")
                break
            
        #Always powerdown the keithley when you are done
        self.powerDownKeithley()
        #Log to the window
        self.log.emit("Finished data taking.")
        
        #Emit to other programs that the daq is done.
        self.done.emit('done')

        #Close the window.
        self.quit()

    def checkGain(self,voltage):
        if voltage > 14:
            print("Gain is too high, dropping",values)
            self.controller.dropGain()
            return False
        return True
    
    def getCurrents(self):
        currents={}
        for channel,voltage in values.items():
            if not self.checkGain(voltage):
                return None
            if not self.debugMode:
                if int(channel[-1]) == 1:
                    print("Controller Resistance: ",self.controller.getResistance())
                currents['V%s'%channel[-1]] = voltage/self.controller.getResistance()
            else:
                currents['V%s'%channel[-1]] = voltage
        return currents['V1']
    
    def getValues(self,volt):
        self.setVoltage(volt)
        keithley=self.readKeithley()
        return -keithley




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
