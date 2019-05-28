from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
from random import random
from contraption import Agilent4155C,Keithley2657a
if __package__ in [None,""]:
    from utilities.controller import Controller
    from utilities.controller_maps import *
else:
    from .utilities.controller import Controller
    from .utilities.controller_maps import *

'''
Things to do:
 - Configure keithley and agilent
 - Provide a software compliance
 - abstract data collection function
 - Wrap arduino?
 - temp write to disk?
'''

#Implements basic agilent, keithley and arduino communications
class BaseProbecardThread(QThread):
    newData=pyqtSignal(float,float,str,bool)
    agilentModes={
        'readCurrent': 'current',
        'readVoltage': 'volt',
    }
    def __init__(self,options):
        super(BaseProbecardThread,self).__init__()
        self.options=options
        self.softCompliance=None #Software compliance
        self.debugMode=options['debug']
        
    def run(self):
        options=self.options
        if self.debugMode:
            print("Skipping device configuration")
            self.agilent=None
            self.keithley=None
            self.controller=None
        else:
            self.initKeithley(compliance=options['kcomp'])
            self.softCompliance=options['kcomp']
            self.initAgilent(options['holdTime'])
            self.controller=Controller(options['com'])

    def initKeithley(self,compliance):
        self.keithley=Keithley2657a()
        self.keithley.configure_measurement(1, 0, float(compliance))

    def initAgilent(self,holdTime):
        self.agilent=Agilent4155C(reset=True)
        self.agilent.setSamplingMode()
        self.agilent.setStandby(True) #Keep circuit open while not reading.
        self.agilent.setLong() #Integration time
        self.agilent.setHoldTime(float(kwargs['holdTime']))

    #Get either voltage or current from agilent
    def readAgilent(self):
        if not self.debugMode:
            return self.agilent.read()

    #Get current from keithley

    def readKeithley(self):
        if not self.debugMode:
            return self.keithley.get_current()

    #Set voltage on powersupply
    def setVoltage(self,volt):
        if not self.debugMode:
            self.keithley.set_output(volt)

    def setCurrentMode(self):
        for i in range(1,5): #Enable all channels
            self.agilent.setCurrent(i,0,float(15))
        self.controller.setCurrentMode()
        
    def setVoltageMode(self,compliance):
        for i in range(1,5): #Enable all channels
            self.agilent.setVoltage(i,0,float(compliance))
        self.controller.setVoltageMode()

    #Get a string representing the current mode
    def getMode(self):
        return list(self.controller.modes)[self.controller.mode]

    #channel must be between 1 and 26
    def setChannel(self,chan):
        self.controller.setChannel(chan)

    #group must be between 1 and 6
    def setGroup(self,group):
        self.controller.setGroup(group)

    #meas is a list of doubles
    #returns a percentage of the measurements that have reaches compliance
    def softwareCompliance(self,meas,compliance):
        if issubtype(type(meas),float): meas=[abs(meas)]
        if self.controller.isMode('voltage'):
            currents=[abs(meas/self.controller.getResistance())]
        else: currents=[abs(I) for I in meas]
        breached=len([I for I in currents if I > abs(compliance)])
        return float(breached)/len(currents)
    
    def getRegions(self):
        #Assuming the region info is in self.options and from RegionWindow.py
        #Filter out all the option with regions_ in the key
        allRegions=[(key,val) for key,val in self.options.items() if 'region_' in key]
        
        #Extract how many regions there are
        nRegions=set( int(key.split('_')[1]) for key,val in allRegions )

        #Prepare an easier data object
        regions=[{} for n in nRegions]
        for key,value in allRegions:
            _,number,phase=key.split('_')
            regions[int(number)][phase]=value

        #Warning: Verify there are no jumps in volts between regions.
        for i,r in enumerate(regions):
            if i==0: continue
            if r['start'] != regions[i-1]['end']:
                print("Regions Check: ",regions)
                raise Exception("Gaps in the voltage regions!")

        #Now you can access regions like:
        # regions[0]['start'] for the first region's start voltage.
        return regions

    def emit(self,volt,value,chan,refresh=True):
        #Emits to the window to plot
        #refresh means the plot will redraw 
        self.newData.emit(volt,value,chan,refresh)

