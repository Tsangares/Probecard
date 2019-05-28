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
    newPoint=pyqtSignal(float,float,str,bool)

    def run(self):
        super(SinglePixelDaq,self).run()
        if not self.debugMode:
            self.setVoltageMode(self.options['acomp'])
            self.controller.setGain(1) #highest resistance
        self.regions=self.getRegions()
        for region in self.regions:
            start=float(region['start'])
            end=float(region['end'])
            steps=int(region['steps'])
            self.sweepRegion(start,end,steps)
            
    def sweepRegion(self,start,end,steps):
        volts=[n*(end-start)/(steps-1)+start for n in range(steps)]
        for volt in volts:
            self.getValues(volt)
        
    def getValues(self,volt):
        #Single Pixel?
        if not self.debugMode:
            self.setVoltage(volt)
            time.sleep(.5)
            current=self.readKeithley()
            voltages=self.readAgilent() #Only need 1 volt value (which channel?)
            
        
    
        
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
