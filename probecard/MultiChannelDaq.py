"""
This is the beast of the multi-channel reading experiment.
Use DEBUG & KEITHLEY to enable and disable testing & debug
When DEBUG is true, no attempt will be made to access visa/gpib devices.
But to be sure ALWAYS disable KEITHLEY when testing.
Dont kill someone by applying a voltage by accident!

When KEITHLEY=False, no voltage will be applied,
but currents from the agilent will be read.
 - WCW 181127
"""

from queue import Queue
from numpy import linspace
from random import random
from io import BytesIO
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton
import json, time
from threading import Thread
from multiprocessing import Process
import matplotlib.pyplot as plt

import statistics as stat
import os

from  contraption.PowerSupply import *
from  contraption.Agilent import Agilent4155C
from  contraption.Arduino import Max
from .interface.DetailWindow import DetailWindow
from .utilities.Excel import writeExcel
from .utilities.emailbot import send_mail

excel_folder = os.path.expanduser("~/Desktop/probecard_output/excel/")
json_folder = os.path.expanduser("~/Desktop/probecard_output/json/")
if not os.path.exists(excel_folder):
    os.makedirs(excel_folder)
if not os.path.exists(json_folder):
    os.makedirs(json_folder)
    
def getChan(chan):
    map={
        25:'E' , 24:'2' , 23:'BB', 22:'AA', 21:'W' ,
        20:'6' , 19:'A' , 18:'1' , 17:'24', 16:'19',
        15:'F' , 14:'B' , 13:'12', 12:'23', 11:'V' ,
        10:'7' ,  9:'11',  8:'13',  7:'14',  6:'18',
         5:'H' ,  4:'M' ,  3:'N' ,  2:'P' ,  1:'U' ,
        99: 'pass-empty', 26: 'pass-guard',
    }
    map2={
        25:'(1,5)' , 24:'(2,5)' , 23:'(3,5)', 22:'(4,5)', 21:'(5,5)' ,
        20:'(1,4)' , 19:'(2,4)' , 18:'(3,4)' , 17:'(4,4)', 16:'(5,4)',
        15:'(1,3)' , 14:'(2,3)' , 13:'(3,3)', 12:'(4,3)', 11:'(5,3)' ,
        10:'(1,2)' ,  9:'(2,2)',  8:'(3,2)',  7:'(4,2)',  6:'(5,2)',
         5:'(1,1)' ,  4:'(2,1)' ,  3:'(3,1)' ,  2:'(4,1)' ,  1:'(5,1)' ,
        99: 'pass-empty', 26: 'pass-guard',
    }
    try:
        return 'Ch%s'%int(map[chan])
    except ValueError:
        return map[chan]
    
#All of the main code is put into a seperate thread to allow
#The UI to not freeze and respond to button clicking like Force Shutdown.
class DaqProtocol(QThread):
    newSample = pyqtSignal(tuple)
    onLog = pyqtSignal(tuple)
    onFinish = pyqtSignal(dict)
    onClearPlot = pyqtSignal(str)
    onCalibrationDone = pyqtSignal(str)
    onEmergencyStop = pyqtSignal(str)

    def __init__(self,options,widget=None):
        super(DaqProtocol,self).__init__(widget)
        self.options=options
        self.calibration=None
        self.calibrated=False
        self.emergencyStop=False
        self.onEmergencyStop.connect(self.initEmergencyStop)
        self.DEBUG=True
        self.KEITHLEY=False
        self.ARDUINO=False

                                     
    def initEmergencyStop(self,msg=None):
        print("Emergency Stop Initialized")
        self.log("Emergency Stop Initialized")
        self.emergencyStop=True
        
    def log(self,*args):
        self.onLog.emit(args)
        
    def run(self):
        if self.calibrated:
            self.collectData(self.options)
            return
        options=self.options
        #Connect to instruments
        port = 0
        self.arduino=None
        if self.options['debug'] == 0:
            #DEBUG IS OFF (DANGEROUS)
            self.DEBUG=False
            self.KEITHLEY=True
            self.ARDUINO=True
        elif self.options['debug'] == 2:
            self.DEBUG=True
            self.KEITHLEY=False
            self.ARDUINO=False

        if not self.DEBUG:
            if self.KEITHLEY:
                self.keithley = Keithley2657a()
                self.configureKeithley(options)
            self.agilent = Agilent4155C(reset=True)
            self.configureAglient(options)
            if self.ARDUINO:
                self.arduino = Max("COM%s"%options['com'])
        self.log("Starting data collection")
        
        self.log("STARTING CALIBRATION")
        self.calibration=self.aquireLoop(0,None,None,self.options['measTime'],int(self.options['repeat']))[0]
        self.onClearPlot.emit("clear")
        self.log("ENDING CALIBRATION")
        
        self.calibrated=True
        self.onCalibrationDone.emit('done')
        #calculate leakage
            
    def getPoint(self):
        return [random(),random(),random(),random()]

    def configureAglient(self, kwargs):
        self.agilent.setSamplingMode()
        self.agilent.setStandby(True)
        self.agilent.setLong()
        #self.agilent.setShort()
        #if int(kwargs['nChan']) < 0 or int(kwargs['nChan']) > 4:
        #    raise Exception("ERROR: Please set number of channels between 0 and 4!")
        #for i in range(1,int(kwargs['nChan'])+1):
        for i in range(1,5): #Enable all channels
            self.agilent.setCurrent(i,0,float(kwargs['acomp']))
        self.agilent.setMedium()
        self.agilent.setHoldTime(float(kwargs['holdTime']))

    def configureKeithley(self, kwargs):
        #Setting the keithley compliance
        #TODO: Check to see if casting caused errors.
        self.keithley.configure_measurement(1, 0, float(kwargs['kcomp']))

    def getMeasurement(self,samples,duration,channels=None,index=None):
        if self.DEBUG:
            time.sleep(.2)
            return {"chan%d"%(i+4*index): 100*random()*i**(i*i) for i in range(1,5)}
        agilentData=self.agilent.read(samples,duration)
        agilent={ getChan(channels[int(key[-1])-1]): value[-1] for key,value in agilentData.items() }
        
        if self.KEITHLEY and index is not None:
            keithley=self.keithley.get_current() #float
            agilent['keithley%d'%index]=keithley
        return agilent

    #collectData    
    def collectData(self, kwargs):
        self.log("Started data collection.".upper())
        print("Started data collection.")
        delay=.1
        allRegionVariables=[(key, val) for key,val in kwargs.items() if 'region' in key]
        regions=[]
        for datum in allRegionVariables:
            key=datum[0]
            val=datum[1]
            for i in range(len(allRegionVariables)):
                if str(i) in key:
                    if len(regions) <= i:
                        for j in range(i-len(regions)+1):
                            regions.append({})
                    regions[i][key[len('region_0_'):]]=val
                    
        measurements=[]
        for i,region in enumerate(regions):
            startVolt=float(region['start'])
            endVolt=float(region['end'])
            steps=int(region['steps'])+1
            step=(endVolt-startVolt)/float(steps)
            #voltages=list(linspace(startVolt,endVolt,steps+1))
            self.log("Region %d initialized with %d steps between %04d and %04g V."%(i,steps,startVolt,endVolt))
            measured=self.aquireLoop(startVolt,step,endVolt,kwargs['measTime'],1)
            measurements+=measured
        measurements=sorted(measurements,key=lambda p: p['Voltage'],reverse=True)
        output=self.repeatedListToDict(measurements)
        if not self.DEBUG and self.KEITHLEY: self.keithley.powerDownPSU()
        #Possibly calculate leakage later?
        if self.emergencyStop: print("Emergency Stop Successful.")
        self.onFinish.emit(output)
        
    #Convert from a repeated list of measurements to a dictionary of channels
    def repeatedListToDict(self,measurements):
        output={}
        for meas in measurements:
            for channel,value in meas.items():
                try:
                    output[channel]
                except KeyError:
                    output[channel]=[]
                output[channel].append(value)
        return output

    #Get resistance from the GUI options or from file.
    def getResistance(self,chan=None):
        #Currently only supporting getting from GUI options
        #The input variable chan here will corespond to the channel
        #Use lookup table to find this resistance.
        return float(self.options['resistance'])
    
    def checkCompliance(self,meas):
        comp=float(self.options['acomp'])
        current=abs(comp/self.getResistance() * .98)
        breached=0
        for key,val in meas.items():
            if abs(val) > current: breached += 1
        proportion=float(breached) / float(len(meas))
        if proportion > .25:
            print("Currently %.02f%% sensors have reaches complaince."%(proportion*100))
        return proportion > .75
    
    def saveDataToFile(self, data):
        filename=self.options['filename']
        with open('%s/%s.json'%(json_folder,filename) ,'w+') as f:
            f.write(json.dumps(data))

    #This is a recursive loop that gathers data & calls itself at the next voltage.
    def aquireLoop(self,volt,step,limit,measTime,repeat=1,delay=.1):
        #Note, if limit is none, then we are calibrating

        ### Logistics and Logging ###
        if self.emergencyStop or (limit is not None and abs(volt) >= abs(limit)):
            self.log("Last voltage measured, ending data collection.")
            return list()

        if limit is not None: self.log("Step is %.02e; while limit is %.02e; currently at %.02e"%(step,limit,volt))

        #Only turn on the keithley if we are absolutley certain we should:
        if not self.DEBUG and self.KEITHLEY and limit is not None:
            self.log("Setting keithley to %.02e"%volt)
            self.keithley.set_output(volt)

        #Repeated measurements is used for averaging.
        if repeat > 1 : self.log("Taking %d measurements on each mux to average."%repeat)
        
        ### Data Taking ###
        meas = {'Voltage': volt}
        time.sleep(float(delay)) #Time between measurements delay
        #for mux in range(0,7):
        for mux in range(0,7): #Mux stands to the range of connected inputs from the multiplexers
            if self.emergencyStop: return []
            if self.ARDUINO and not self.DEBUG: self.arduino.getGroup(mux)
            channels=Max.reverse_map[mux]
            self.log("Set mux to %d, reading channels: %s"%(mux,channels))
            if not self.DEBUG: time.sleep(1) #Delay for multiplexers to settle
            cache={} #Cache is the measurement for a specific mux
            for i in range(repeat): #This supports repeated measurements for averaging measurements
                if i < repeat and repeat is not 1: self.log("On sample %d out of %d. %2d%%"%(i,repeat,100.0*i/repeat))
                thisMeasurements=self.getMeasurement(1,measTime,channels,index=mux)
                for channel,value in thisMeasurements.items():
                    if "keithley" in channel:
                        amps=value
                    else:
                        ## Convert keithley voltage to current ##
                        amps=value/self.getResistance(channel)

                        ## Account for noise ##
                        if self.calibration is not None:
                            amps -= self.calibration[channel]
                    try:
                        cache[channel].append(amps)
                    except KeyError:
                        cache[channel]=[]
                        cache[channel].append(amps)
                    self.log("Chan %s reads %.03e A"%(channel,amps))
            cache={key: stat.mean(vals) for key,vals in cache.items()}
            if repeat is 1 and limit is not None: self.newSample.emit((volt,cache))
            #Appends cache to measurements
            meas={**meas, **cache}
        ## Finalize ##
        self.saveDataToFile(meas)
        if limit is None: return [meas] #limit is None implies this is calibration mode
        elif abs(limit-volt)/step > 10 and self.checkCompliance(meas):
            print("Compliance Breached! Taking 8 more measurements.")
            newLimit=volt+step*9
            return self.aquireLoop(volt+step,step,volt+step*9,measTime,repeat,delay).append(meas)
        else:
            newLimit=limit
            print("Acquisition cycle on %04d V ended. Makeing volt step of %.02f"%(int(volt),step))
        return self.aquireLoop(volt+step,step,newLimit,measTime,repeat,delay)+[meas]

    #returns the second item in this weird format.
    def skipMeasurements(result, skip):
        output={}
        for key in result:
            currents=result[key][skip:]
            if len(currents) == 1:
                output[key]=currents[0]
            else:
                output[key]=currents
        return output


#Just a window now.
class MultiChannelDaq(DetailWindow):
    onFinish = pyqtSignal(str)
    def __init__(self, options):
        super(MultiChannelDaq,self).__init__()
        #Build number of plots
        #for i in range(1,5):
        #    self.figs.append(self.figure.add_subplot(2,2,i))
        self.fig=self.figure.add_subplot(1,1,1)
        self.show()
        self.options=options
        #Starts the protocol thread
        self.thread=DaqProtocol(options,self.mainWidget)
        self.thread.newSample.connect(self.addPoint)
        self.thread.onLog.connect(self.log)
        self.thread.onClearPlot.connect(self.clearPlot)
        self.thread.onFinish.connect(self.finalizeData)
        self.thread.onCalibrationDone.connect(self.afterCalibration)
        self.thread.start()
        
    def afterCalibration(self,msg=None):
        start=QPushButton("Start")
        self.menuLayout.insertRow(0,start)
        start.clicked.connect(self.startExperiment)
        
    def startExperiment(self,msg=None):
        shutdown=QPushButton("Force Shutdown")
        shutdown.clicked.connect(lambda: self.thread.onEmergencyStop.emit('stop'))
        self.menuLayout.removeRow(0)
        self.menuLayout.insertRow(0,shutdown)
        self.thread.start()
        
    def finalizeData(self,data):
        files=[]
        filename=writeExcel(data,self.options['filename'],excel_folder=excel_folder)
        print("Wrote excel.")
        imgdata = BytesIO()
        self.figure.savefig(imgdata, format='png')
        imgdata.seek(0)
        files.append((imgdata.getbuffer(), "log"))
        print("Saved plot.")
        send_mail(filename,self.options['email'],files=files)
        print("Sent mail.")
        self.onFinish.emit('done')
        self.close()


