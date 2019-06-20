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
    log=pyqtSignal(str)
    done=pyqtSignal(str)
    currentVoltage=pyqtSignal(float)
    rampRate=2.0
    agilentModes={
        'readCurrent': 'current',
        'readVoltage': 'volt',
    }
    def __init__(self,options,enableAgilent=True):
        super(BaseProbecardThread,self).__init__()
        self.options=options
        self.softCompliance=None #Software compliance
        self.debugMode=options['debug']
        self.enableAgilent=enableAgilent
        self.forceStop=False
        
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
            if self.enableAgilent:
                self.initAgilent(options['holdTime'])
            self.controller=Controller(options['com'])

    def stop(self):
        self.forceStop=True

    def powerDownKeithley(self):
        if not self.debugMode:
            self.log.emit("Powering down the power supply at a rate of %.02fV/s"%self.rampRate)
            self.keithley.powerDownPSU(self.rampRate)

    def initKeithley(self,compliance):
        self.keithley=Keithley2657a()
        self.keithley.configure_measurement(1, 0, float(compliance))

    def initAgilent(self,holdTime):
        self.agilent=Agilent4155C(reset=True)
        self.agilent.inst.timeout=3000
        self.agilent.setSamplingMode()
        self.agilent.setStandby(True) #Keep circuit open while not reading.
        self.agilent.setLong() #Integration time
        self.agilent.setSampleSize(1)
        self.agilent.setHoldTime(float(self.options['holdTime']))

    #Get either voltage or current from agilent
    #Returns a dict of the form {'I1': .03,'V2': 1.3,'V3': .1,'I4': .55}
    #Where I1 means it is reading current on channel 1.
    def readAgilent(self):
        if not self.debugMode:
            #return self.agilent.read()
            return {k: v[0] for k,v in self.agilent.read().items()}
        else:
            sleep(.2)
            return {'V%d'%i: random() for i in range(1,5)}

    #Returns an array size 4 representing the values from the agilent
    def getAgilentValues(self,verbose=False):
        output=[None for i in range(4)] #Initilaize array with values
        values=self.readAgilent()
        if verbose: print(values)
        for key,value in values.items():
            index=int(key[-1])-1 #Extract index from key
            output[index]=value #Place value in array while keeping order
        return output
    
    #Get current from keithley
    def readKeithley(self):
        if not self.debugMode:
            return self.keithley.get_current()
        else:
            sleep(.2)
            return random()

    #Set voltage on powersupply
    def setVoltage(self,volt):
        if not self.debugMode:
            self.keithley.set_output(volt)
        delay=2.0/10.0
        print("Delay for %.02f secconds"%delay)
        sleep(delay)
        self.log.emit("Voltage set to %s"%volt)

    #Set current mode on the controller and ready to read current from the agilent
    def setCurrentMode(self,compliance):
        for i in range(1,5): #Enable all channels
            self.agilent.setVoltage(i,0,compliance)
        self.controller.setCurrentMode()

    #Set voltage mode on the controller and ready to read voltage from the agilent
    def setVoltageMode(self):
        for i in range(1,5): #Enable all channels
            self.agilent.setCurrent(i,0,float(15))
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
        if issubclass(type(meas),float): meas=[abs(meas)]
        currents=[abs(I) for I in meas]
        breached=len([I for I in currents if I >= abs(compliance*.95)])
        return float(breached)/len(currents)

    def emit(self,volt,value,chan,refresh=True):
        #Emits to the window to plot
        #refresh means the plot will redraw 
        self.newData.emit(volt,value,chan,refresh)

    #Converts the region data into a list of all the voltages to step through
    def getVoltageRegions(self):
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

        voltages=[]
        for region in regions:
            start=float(region['start'])
            end=float(region['end'])
            steps=int(region['steps'])
            volts=[n*(end-start)/(steps)+start for n in range(steps)]
            voltages+=volts
        voltages.append(float(regions[-1]['end']))
        return voltages

