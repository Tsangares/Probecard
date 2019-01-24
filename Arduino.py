# this version uses Arduino sketch "ProbeCard_CH4"
# first step in converting program to functions.
import serial
import time
import sys
import struct
class Max:
    reverse_map = {
            #key: lower multiplexer address, value: channels output to J1, J2, J3, and J4
            # in order.  all channels are routed through four 8:1 multiplexers with four
            # outputs routed to output connectors J1-J4.  All four multiplexers are controlled
            # by one three bit address.
            0: (1, 7, 13, 19),
            1: (2, 8, 14, 20),
            2: (3, 9, 15, 21),
            3: (4, 10, 16, 22),
            4: (5, 11, 17, 23),
            5: (6, 12, 18, 24),
            6: (26, 99, 99, 25)
        }
    channel_map = {
            # key: channel number, value: (low multiplexer address, high multiplexer address)
            # HPK 5x5 sensor pads are labeled channel 1 - 25. Channel 26 is the bias ring.
            1: (0,0),
            2: (1, 0),
            3: (2, 0),
            4: (3, 0),
            5: (4, 0),
            6: (5, 0),
            7: (0, 1),
            8: (1, 1),
            9: (2, 1),
            10: (3, 1),
            11: (4, 1),
            12: (5, 1),
            13: (0, 2),
            14: (1, 2),
            15: (2, 2),
            16: (3, 2),
            17: (4, 2),
            18: (5, 2),
            19: (0, 3),
            20: (1, 3),
            21: (2, 3),
            22: (3, 3),
            23: (4, 3),
            24: (5, 3),
            25: (6, 3),
            26: (6, 0)
        }
    def __init__(self,port=None):
        self.selectError=["channel number out of range","Quitting: Nothing read back","Quitting: Timeout Error on readback","address read back from Arduino doesn't match address sent"]
        
        self.port=port
        self.ArduinoSerial = None
        if port is not None: self.ArduinoSerial = self.open_com( port )
        else: self.ArduinoSerial = None
        
        if (self.ArduinoSerial == -1):
            raise Exception("Arduino ERROR (COM): couldn't open port ", port )

    def connect( self,port ):
        self.ArduinoSerial = self.open_com( port )
        return self.ArduinoSerial != -1
    
    def getChannel( self,chan ):
        return_code = self.select_channel( self.ArduinoSerial, chan )
        if return_code is None: return None
        else: raise Exception( "Arduino ERROR (CHAN):",self.selectError[return_code] )
        
    def getGroup( self,group ):
        return_code = self.select_channel_group( self.ArduinoSerial, group )
        if return_code is None: return None
        else: raise Exception( "Arduino ERROR (CHAN):",self.selectError[return_code] )
        
    def open_com( self,port ):
        #open COM port with 5 second timeout
        try:
            ArduinoSerial = serial.Serial(port,9600,timeout=5)
        except serial.SerialException:
            return -1
        time.sleep(2)
        # for debugging, verify that port is open, and parameters correct
        #print(ArduinoSerial)
        return ArduinoSerial

    def write(self, string):
        if self.ArduinoSerial is not None:
            self.ArduinoSerial.write(string)
        else:
            print("Please setup the arduino before writing to it.")
            
    def select_channel_group(self, ArduinoSerial, mux_address):
        #convert mux address (in Unicode string) to integer
        a = int(mux_address)
        if (a<0 or a>6):
            raise Exception("ARDUINO ERROR: Mux index is out of bounds!")
            #sys.exit(5)
        #convert integer into packed binary.  
        # ">" indicateds "big-endian" bit order
        # "B" indicates Python integer of one byte size.
        # this will leave high order bits = 0, which will not effect the result
        b = struct.pack('>B',a)
        #display byte to send in hex for debugging
        #print("byte to send: ", hex(b[0]) )     
        #write to Arduino
        ArduinoSerial.write(b)
        # arduino will do a serial.read() and put result into an integer variable
        #arduino will send the byte it received back as confirmation that the address was received
        # it will then separate out the address bits and update digital outputs if needed.
        # arduino also handles multiplexer enable lines locally.  
        try:
            x = ArduinoSerial.read()
            #if the Arduino doesn't answer immediately, serial read returns nothing and
            # program proceeds to next instruction.  Timeout set to 5 seconds doesn't make
            # a difference, so there should never be timeout errors.  
            if(x == b''):  # i.e. if nothing read back
               raise Exception("ARDUINO ERROR: Nothing read back!")
               #sys.exit(2)
        except TimeoutError:
            raise Exception("ARDUINO ERROR: Timeout!")
            #sys.exit(3)
        #print byte received for debugging
        #print("byte received :", hex(x[0]) )
        # if byte read back is different from byte sent, halt and catch fire
        if (x != b):
            # for debugging
            #print("error:  byte sent: ",hex(f[0]) ," byte received: ", hex(x[0]) )
            raise Exception("ARDUINO ERROR: debugging!")
            #sys.exit(4)
        #else: print("Correct bits received from Arduino")
        #return tuple containing channel numbers
            
    def select_channel( self,ArduinoSerial, channel_no=None, mux=None ):
        #convert channel number (in Unicode string) to integer
        a = int(channel_no)
        if (a < 1 or a > 26):
            return 1
            # lookup low and high multiplexer addresses for the channel
        
        b = self.channel_map[a]
        # print multiplexer addresses for debugging
        #print("corresponding addresses: ", b)
        # pack addresses into one byte
        c = b[0]
        d = b[1]
        d = d << 4
        e = c|d
        #convert integer into packed binary.  
        # ">" indicateds "big-endian" bit order
        # "B" indicates Python integer of one byte size.
        f = struct.pack('>B',e)
        #display byte to send in hex for debugging
        #print("byte to send: ", hex(f[0]) )     
        #write to Arduino
        ArduinoSerial.write(f)
        # arduino will do a serial.read() and put result into an integer variable
        #arduino will send the byte it received back as confirmation that the address was received
        # it will then separate out the address bits and update digital outputs if needed.
        # arduino also handles multiplexer enable lines locally.  
        try:
            x = ArduinoSerial.read()
            #if the Arduino doesn't answer immediately, serial read returns nothing and
            # program proceeds to next instruction.  Timeout set to 5 seconds doesn't make
            # a difference, so there should never be timeout errors.  
            if(x == b''):  # i.e. if nothing read back
                return 2
        except TimeoutError:
            return 3
            #print byte received for debugging
            #print("byte received :", hex(x[0]) )
            # if byte read back is different from byte sent, halt and catch fire
        if (x != f):
            # for debugging
            #print("error:  byte sent: ",hex(f[0]) ," byte received: ", hex(x[0]) )
            return 4
            #else: print("Correct bits received from Arduino")
        return None
            
