import serial
from serial import SerialException
import time
import sys
import struct
import array
from controller_maps import PAD,INVERT,MUX,reverse_channel_map

class Controller:
    class OP_CODE:
	SET_GAIN = 0
	WRITE_SR = 1
	SET_CURRENT_MODE = 2
	SET_CAL_MODE = 3
	SET_VOLTAGE_MODE = 4
	RESET = 5
	READ_SR = 6
	SET_DISABLE_MUX = 7
	NAME=8
    VOLTAGE_MODE=0
    CURRENT_MODE=1
    CAL_MODE=2
    ALL_PADS_GROUNDED=3
    def __init__(self,port):
        self.MODE = 0
        # serial shift register data, and data in "packed" form
        sr_data = 0
        p_sr_data = 0
        
        # selected gain resistor for current to voltage converter.  The default is resistor R5, currently configured to 15 MOhms.
        gain = 5

        # selected channel number.  valid channel number are 1-26.  '0' indicates no individual channel selected
        chan = 0

        # channel group selected for readout, and list of channels in that group
        group = 0
        channels = {}
        self.connection=Controller.open_com(port)
    def setVoltageMode(self):
        MODE=self.VOLTAGE_MODE
        self.write_byte(OP_CODE.SET_VOLTAGE_MODE)
    def setCurrentMode(self):
        MODE=self.CURRENT_MODE
        self.write_byte(OP_CODE.SET_CURRENT_MODE)
    def setCalMode(self):
        MODE=self.CAL_MODE
        self.chan=0
        self.channels={}
        self.write_calibration()
    def setGroundMode(self):
        MODE=self.ALL_PADS_GROUNDED
        """NEED TO WRITE: Look at maxes CLI"""
        pass

    
    def isConnected(self):
        return "ATmega32U4_5V_16MHz" in self.write_byte(OP_CODE.NAME)
        
    def write_byte(self, data):
        global debug
        a= int(data)
        p_data = struct.pack('>B', a)
        if (debug == 1): print("opcode: ", p_data)
        self.connection.write(p_data)
        data_read = self.connection.read()
        if(p_data != data_read):
            if(debug ==1):
                print("data read: ", data_read)
            print("failed to write byte")
            exit(-1)
        return data_read

        
    def open_com(port):
        #open COM port with 5 second timeout
        try:
            connection = serial.Serial(port,9600,timeout=5)
        except SerialException:
            return -1
        time.sleep(2)
        return connection

    def write_gain(self,gain):
        # write op code = 0  - select gain resistor in current to voltage converter
        self.write_byte('0')
        # write gain (1, 2, 3, 4, 5) to Arduino
        self.write_byte(gain)

    def ground_all_pads(self,disableMultiplexers):
        global sr_data
        MODE = ALL_PADS_GROUNDED
        if disableMultiplexers:
            self.write_byte(7)
        sr_data = 0
        sr_data_mod = sr_data ^ INVERT
        self.write_serial_register(sr_data_mod)

    def write_serial_register(self,sr_data_mod):
        # write opcode 1 - write four bytes to serial shift register
        # note: this function writes given data to serial shift register without inverting bits
        # inversion is done by calling code.
        self.write_byte(1)
        # convert number (in Unicode string) to integer, if integer already, next step will do no harm
        a = int(sr_data_mod)
        # convert integer into packed binary.  
        # ">" indicateds "big-endian" bit order
        # "B" indicates Python integer of one byte size.
        # "i" indicates four byte integer
        p_sr_data_mod = struct.pack('>i',a)
        # display bytes to send in hex for debugging
        if (debug == 1):
            print("data sent: ")
            a=int(sr_data_mod)
            b=format(a, "b").rjust(31, '0')
            print("sr_data  ", b)

        # write data to Arduino
        self.connection.write(p_sr_data_mod)
        # read back for verification
        sr_data_read=self.connection.read(4)
        if (debug == 1):
            print("sr data read back: ")
            #convert bytes to int
            a = int.from_bytes(sr_data_read, byteorder='big', signed=False)
            b=format(a, "b").rjust(31, '0')
            print("sr_data  ", b)
        
        if(p_sr_data_mod != sr_data_read):
            print("failed to write serial shift register data")
            exit(-1)
    

    def write_calibration(self):
        # set CAL_MODE.  
        global chan, channels, sr_data
        chan = 0
        channels = {}
        # set Pro Micro in cal mode.  EN line is set low, disconnecting lower mux tier from OUTA - OUTD
        # set EN2 high, connecting OUTA-OUTD to current to voltage converter
        self.write_byte(3)
        # set lower tier mux address to 111, selecting GND to put it, and pcb traces in a known state
        # set upper tier mux address to 00, selecting OUTA, wich will be used for current input to
        # current to voltage coverter, allowing calibration of this stage.
        # sr_data must be altered, so for simplicity, channel data is zeroed out.
        # this requires channel to be re-selected after calibration.
        #
        # note that the current to voltage converter cal also be calibrated in voltage mode, with current injected
        # in the input pin array.  This puts input switches and multiplexers into the circuit with their leakage currents.
        # these must be included in calibration to get a realistic ofset voltage.
        # this separate calibration mode is included to study the current to voltage converter with only second tier mux
        # leakage included. may be used on the fly to check amplifier offset voltage when a sensor is being probed.
        # afterthought: put a three pin header on the amplifier input, to select either multiplexer outputs, or separate cal input.
        sr_data = 0
        sr_data = 3 << 26
        sr_data_mod = sr_data
        sr_data_mod = sr_data_mod ^ INVERT
        # print("sr_data = ", format(sr_data_mod, "b"))
        self.write_serial_register(sr_data_mod)
 



