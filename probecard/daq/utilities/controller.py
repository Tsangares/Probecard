import serial
from serial import SerialException
import time
import sys
import struct
import array
if __package__ in [None,""]:
    from controller_maps import PAD,INVERT,MUX,reverse_channel_map
    from magnitudes import SI
else:
    from .controller_maps import PAD,INVERT,MUX,reverse_channel_map
    from .magnitudes import SI

class Resistor:
    R1 = 15_000_000
    R2 =  1_500_000
    R3 =    150_000
    R4 =     15_000
    R5 =      1_500
    unit='ohms'
    resistances=R=[R1,R2,R3,R4,R5]
    reverseLabels={SI(r): r for r in R}
    labels=[SI(r) for r in R]
    
class Controller:
    OP_CODE={
	'SET_GAIN': 0,
	'WRITE_SR': 1,
	'SET_CURRENT_MODE': 2,
	'SET_CAL_MODE': 3,
	'SET_VOLTAGE_MODE': 4,
	'RESET': 5,
	'READ_SR': 6,
	'SET_DISABLE_MUX': 7,
	'NAME': 8,
    }
    modes={
        'voltage': 0,
        'current': 1,
        'calibration': 2,
        'grounded': 3,
    }
    INVERT = int('10110110110110110110110111',2)
    
    def __init__(self,port):
        #Connect to port.
        self.mode = None
        self.gain = None
        self.connection=Controller.connect(port)

    def isMode(self,mode):
        return self.mode==self.modes[mode]

    def setVoltageMode(self):
        if not self.isMode('voltage'):
            self.mode=self.modes['voltage']
            self.writeByte(self.OP_CODE['SET_VOLTAGE_MODE'])
            
    def setCurrentMode(self):
        if not self.isMode('current'):
            self.mode=self.modes['current']
            self.writeByte(self.OP_CODE['SET_CURRENT_MODE'])
            
    def setGroundMode(self,disableMultiplexers=True):
        if not self.isMode('grounded'):
            self.mode=self.modes['grounded']
            if disableMultiplexers:
                self.writeByte(self.OP_CODE['SET_DISABLE_MUX'])
            self.writeSerialRegister(0 ^ self.INVERT)

    def setCalMode(self):
        if not self.isMode('calibration'):
            self.mode=self.modes['calibration']
            self.writeByte(self.OP_CODE['SET_CAL_MODE'])
            sr_data = 3 << 26
            sr_data_mod = sr_data ^ self.INVERT
            self.writeSerialRegister(sr_data_mod)

    def dropGain(self):
        if self.gain+1 > 5:
            print("GAIN is too high but cannot drop any farther!")
        #Maybe a dangerous to just break if the gain is out of range?
        self.setGain(self.gain+1)
        
    #Sets the gain resistor (See resistor class in controller_maps).
    def setGain(self,gain):
        if gain<1 or gain>5: raise Exception("Resistance out of range.")
        self.writeByte(self.OP_CODE['SET_GAIN'])
        self.writeByte(gain)
        self.gain=gain
        return self.getResistance()
        #Q: Dose this revert back to current/voltage mode?

    def getResistance(self):
        return Resistor.resistances[self.gain-1]
        
        
    #Automatically switches to voltage mode!
    def setChannel(self,chan):
        self.setVoltageMode()
        if chan<1 or chan>26: raise Exception("Channel out of range")
        sr_data = MUX[chan] | PAD[chan]
        sr_data_mod = sr_data ^ self.INVERT
        self.writeSerialRegister(sr_data_mod)
        print("Set channel to", chan)
        
    #Automatically switches to current mode!
    def setGroup(self,group):
        self.setCurrentMode()
        if group<0 or group>6: raise Exception("Mux out of range")
        channels=reverse_channel_map[group]
        sr_data=0
        for chan in list(channels):
            if chan==99: continue
            sr_data = sr_data | PAD[chan]
        sr_data = sr_data | MUX[channels[0]]
        sr_data_mod = sr_data ^ self.INVERT
        self.writeSerialRegister(sr_data_mod)
        print("Set group to", group)

    #This function only works on the most recent probcard skratch
    def isConnected(self):
        return "ATmega32U4_5V_16MHz" in self.writeByte(self.OP_CODE['NAME'])

    #Fundamental writing function
    def writeByte(self, data):
        p_data = struct.pack('>B', data)
        self.connection.write(p_data)
        data_read = self.connection.read()
        if p_data != data_read:
            raise Exception("Failed to write byte.",data_read)
        return data_read

    def connect(port):
        if 'COM' not in port:
            port="COM%s"%port
        try:
            connection = serial.Serial(port,9600,timeout=5)
        except SerialException:
            raise Exception("Failed to connect to controller. Check port")
        time.sleep(2)
        return connection

    def writeSerialRegister(self,sr_data_mod):
        self.writeByte(self.OP_CODE['WRITE_SR'])
        a = sr_data_mod
        # convert integer into packed binary.  
        # ">" indicateds "big-endian" bit order
        # "i" indicates four byte integer
        p_sr_data_mod = struct.pack('>i',a)
        self.connection.write(p_sr_data_mod)
        sr_data_read=self.connection.read(4)
        if(p_sr_data_mod != sr_data_read):
            raise Exception("failed to write serial shift register data")
    

 



