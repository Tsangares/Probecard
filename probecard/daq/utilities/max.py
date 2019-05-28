# this program talks to HPK-5x5_V7.0j readout board,
# using Arduino sketch "serial_test_V4"
# it controls current to voltage gain, or writes four bytes to Arduino, which sends it to a serial to parallel shift
#register, which in turn sets mux addresses and selects channel(s) to be read out.
# first step in converting program to functions.
import serial
from serial import SerialException
import time
import sys
import struct
import array

# The readout system has four operating modes:
# single channel readout with current to voltage translation
# readout of four channels at a time, as currents
# calibration of current to voltage converter
# total sensor current test.  ground all sensor pads and measure total current of high voltage supply.
# Pro Micro software impliments voltage and current modes.  The python MODE variable is just to keep track of what state
# the Pro Micro is in, so that the user can be informed of it.  
MODE = 0; 
VOLTAGE_MODE = 0
CURRENT_MODE = 1
CAL_MODE = 2
ALL_PADS_GROUNDED = 3

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

# channel map for 32 bit serial shift register
# to read out pad n, PAD[n] sets correct ssr bit high to switch channel n from ground to readout
# note: pads are labeled as in previous readout systems.  
# this array is an array of bit masks
# this mapping is valid for HPK-5x5 readout board V7.0j
# note: channel 26 is the guard ring
# create array and initialize to zero.  Then load with valid map
PAD = array.array('i',(0 for i in range(0,27)))
PAD[1] = 1 << 10
PAD[2] = 1 << 5
PAD[3] = 1 << 6
PAD[4] = 1 << 7
PAD[5] = 1 << 2
PAD[6] = 1 << 14
PAD[7] = 1 << 18
PAD[8] = 1 << 19
PAD[9] = 1 << 21
PAD[10] = 1 << 22
PAD[11] = 1 << 9
PAD[12] = 1 << 15
PAD[13] = 1 << 17
PAD[14] = 1 << 0
PAD[15] = 1 << 3
PAD[16] = 1 << 16
PAD[17] = 1 << 11
PAD[18] = 1 << 23
PAD[19] = 1 << 1
PAD[20] = 1 << 20
PAD[21] = 1 << 8
PAD[22] = 1 << 13
PAD[23] = 1 << 12
PAD[24] = 1 << 25
PAD[25] = 1 << 4
PAD[26] = 1 << 24
#PAD=[None,10,5,6,7,2,14,18,19,21,22,9,15,17,0,3,16,11,23,1,20,8,13,12,25,4,24]
#PAD=[1<<p for p in PAD if p is not None]

# SPDT switches are miswired on 2/3 of the channels.  normall select line low will short pad to ground, but in
# miswired channels, low select line connects pads to multiplexer array.  The mask below should invert selected bits in serial
# register data when exclusive ored with original data.
# convert binary string to decimal number
# the general strategy is to maintain serial shift register data without inverting bits, make a copy, invert
# bits in the copy, and write that to serial shift register.  
INVERT = int('10110110110110110110110111',2)


# multiplexer address bits.  to read out pad n, find correct address bits in MUX[n]
# MUX contains address bits A4-A0, which reside in bits 31:27 of the shift register
# create array and initialize to zero.  Then load with valid map.
# take address bits A4-A0 as a decimal number, and bit shift 26 bits
MUX = array.array('i',(0 for i in range(0,27)))
MUX[1] = 1 << 26
MUX[2] = 24 << 26
MUX[3] = 0 << 26
MUX[4] = 25 << 26
MUX[5] = 27 << 26
MUX[6] = 9 << 26
MUX[7] = 13 << 26
MUX[8] = 11 << 26
MUX[9] = 19 << 26
MUX[10] = 21 << 26
MUX[11] = 3 << 26
MUX[12] = 10 << 26
MUX[13] = 12 << 26
MUX[14] = 29 << 26
MUX[15] = 26 << 26
MUX[16] = 8 << 26
MUX[17] = 5 << 26
MUX[18] = 17 << 26
MUX[19] = 30 << 26
MUX[20] = 20 << 26
MUX[21] = 2 << 26
MUX[22] = 4 << 26
MUX[23] = 6 << 26
MUX[24] = 18 << 26
MUX[25] = 28 << 26
MUX[26] = 16 << 26

reverse_channel_map = {
    #key: lower multiplexer address, value: channels output to J2, J5, J3, and J6
    # in order.  all channels are routed through four 8:1 multiplexers with four
    # outputs routed to the above output connectors.  All four multiplexers are controlled
    # by one three bit address.
    0: (3, 16, 26, 2),
    1: (1, 6, 18, 4),
    2: (21, 12, 24, 15),
    3: (11, 8, 9, 5),
    4: (22, 13, 20, 25),
    5: (17, 7, 10, 14),
    6: (23, 99, 99, 19)
}

def open_com( port ):
    #open COM port with 5 second timeout
    try:
        ArduinoSerial = serial.Serial(port,9600,timeout=5)
    except SerialException:
        return -1
    time.sleep(2)
    return ArduinoSerial


def write_gain(ArduinoSerial, gain ):
    # write op code = 0  - select gain resistor in current to voltage converter
    write_byte(ArduinoSerial, '0')
    # write gain (1, 2, 3, 4, 5) to Arduino
    write_byte(ArduinoSerial, gain)

def ground_all_pads(ArduinoSerial):
    global sr_data
    MODE = ALL_PADS_GROUNDED
    a=input("disable multiplexers? (y,n)")
    if (a == 'y'):
        write_byte(ArduinoSerial, 7)
        
    sr_data = 0
    sr_data_mod = sr_data ^ INVERT
    write_serial_register(ArduinoSerial, sr_data_mod)

def write_serial_register( ArduinoSerial, sr_data_mod):
    # write opcode 1 - write four bytes to serial shift register
    # note: this function writes given data to serial shift register without inverting bits
    # inversion is done by calling code.
    write_byte(ArduinoSerial, 1)
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
    ArduinoSerial.write(p_sr_data_mod)
    # read back for verification
    sr_data_read=ArduinoSerial.read(4)
    if (debug == 1):
        print("sr data read back: ")
        #convert bytes to int
        a = int.from_bytes(sr_data_read, byteorder='big', signed=False)
        b=format(a, "b").rjust(31, '0')
        print("sr_data  ", b)
        
    if(p_sr_data_mod != sr_data_read):
        print("failed to write serial shift register data")
        exit(-1)
    

def write_calibration( ArduinoSerial):
    # set CAL_MODE.  
    global chan, channels, sr_data
    chan = 0
    channels = {}
    # set Pro Micro in cal mode.  EN line is set low, disconnecting lower mux tier from OUTA - OUTD
    # set EN2 high, connecting OUTA-OUTD to current to voltage converter
    write_byte(ArduinoSerial, 3)
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
    write_serial_register(ArduinoSerial, sr_data_mod)
 

def write_byte(ArduinoSerial, data):
    global debug
    a= int(data)
    p_data = struct.pack('>B', a)
    if (debug == 1): print("opcode: ", p_data)
    ArduinoSerial.write(p_data)
    data_read = ArduinoSerial.read()
    if(p_data != data_read):
        if(debug ==1):
            print("data read: ", data_read)
        print("failed to write byte")
        exit(-1)

def help():
    print("enter opcode: ")
    #print(" V   - enable voltage readout")
    #print(" I   - enable current readout")
    print(" cal - enable calibration of current to voltage amplifier")
    #--print(" w   - write data to serial shift register (debugging tool")
    #print(" g   - select current to voltage gain resistor number")
    #print(" gr  - select channel group to read out in current mode")
    print(" w   - write user provided number to serial shift register")
    #print(" ch  - select channel i for readout")
    print(" d   - toggle debug variable")
    print(" gnd - ground all pads; optionally disable multiplexers")
    print(" s   - display current settings")
    print(" r   - reset hardware")
    print(" h   - help")
    print(" q   - quit")
    #--print(" re  - read back serial shift register data from Pro Micro (debugging tool)")

    
# main program
debug = 1

# N = com port number
if (len(sys.argv) != 2):
    print("syntax: Write_serial_sr.py COMN")
    sys.exit()

# get com port
port = sys.argv[1]
ArduinoSerial = open_com( port )
if (ArduinoSerial == -1):
    print("couldn't open ", port )
    sys.exit()
    
while 1:
    # get operation code for Arduino
    print("enter h for help, q for quit")
    data = input("opcode? ")
    if (data == 'q'):
        break
    
    if (data == 'V'):
        # set up to connect individual channels to current to voltage converter.  Readout is a voltage.
        print("enable voltage readout mode")
        MODE = VOLTAGE_MODE
        write_byte(ArduinoSerial, 4)
        
    if (data == 'I'):
        # set up to connect groups of four channels to outputs OUTA-OUTD, to be read out as currents.
        print("setting current readout mode")
        MODE = CURRENT_MODE
        write_byte(ArduinoSerial, 2)
        
    if (data == 'g'):
        # select gain resistor to use in current to voltage converter
        gain = input("enter gain setting (1, 2, 3, 4, 5 refers to resistor to select, not gain as such): ")
        print("setting gain to: ", gain)
        write_gain(ArduinoSerial, gain )
        
    if (data == 'cal'):
        # disconnect all channels from current to voltage converter
        # connects OUTA output to current to voltage converter.
        # connect external current source to OUTA, measure voltage out vs. current in
        print("configure for calibration")
        chan = 0
        channels = {}
        MODE = CAL_MODE
        write_calibration(ArduinoSerial)
        
    if (data == 'w'):
        # this is a debugging tool.  write user specified data to serial shift register
        # bits are not inverted with INVERT mask.  sr_data is not altered.
        chan = 0
        channels = {}
        sr_data_test = input("enter sr data (or q for quit): ")
        # write data number to Arduino
        write_serial_register( ArduinoSerial, sr_data_test )
        
    if (data == 'd'):
        # enables printing of extra data while program executes
        if (debug == 1): debug = 0
        elif (debug == 0): debug = 1
        print("debug set to: ", debug)

    if (data == 're'):
        # debugging tool to read back serial shift register data from Pro Micro.
        # this doesn't work.  I read back zero no matter what.  
        write_byte(ArduinoSerial, 6)
        sr_data_read = -1
        # see if there are 4 bytes in the input buffer waiting to be read
        if(ArduinoSerial.inWaiting() == 4):
            sr_data_read = ArduinoSerial.read(4)

        #convert bytes to int
        a = int.from_bytes(sr_data_read, byteorder='big', signed=False)
        # write data as a binary string, right adjusted, padded with zeros on the left
        b=format(a, "b").rjust(31, '0')
        print("sr_data: ", b)
        a = a^INVERT
        b=format(a, "b").rjust(31, '0')
        print("decoded: ", b)
        
    if (data == 'ch'):
        # select a single channel for readout in voltage mode.  alters sr_data.
        if (MODE != VOLTAGE_MODE):
            print("switching to voltage readout")
            MODE = VOLTAGE_MODE
            write_byte(ArduinoSerial, 4)
        channels = {}
        chan = input("enter channel number (1-26): ")
        n = int(chan)
        if (n < 1 or n > 26):
            print("channel number out of range")
            exit(-1)

        # set serial shift register bits to connect the selected channel to curret to voltage converter
        sr_data = MUX[n] | PAD[n]
        if (debug == 1): print("uninverted sr_data: ", sr_data)
         # invert selected channels    
        sr_data_mod = sr_data ^ INVERT
        if (debug == 1):
            print("inverted sr_data:  ", sr_data_mod)
            print("sr_data: ", sr_data);
        write_serial_register(ArduinoSerial, sr_data_mod)

    if (data == 'gr'):
        print("switching to current readout")
        MODE = CURRENT_MODE
        chan = 0
        write_byte(ArduinoSerial, 2)
        mux_add = input("enter mux address: ")
        group = int(mux_add)
        if (group < 0 or group > 6):
            print("mux address out of range")
            exit(-1)
            
        channels = reverse_channel_map[group]
        print("channels to read out: ", channels)
        sr_data = 0      
        for i in range(0, 4):
            # select all four channels for readout.
            if (channels[i] != 99):
                if (debug == 1):
                    print("turning on channel: ", channels[i])
                    a=int(sr_data)
                    b=format(a, "b").rjust(31, '0')
                    print("sr_data  ", b)                  
                    a=int(PAD[ channels[i] ])
                    b=format(a, "b").rjust(31, '0')
                    print("PAD:     ", b)
                          
                sr_data = sr_data | PAD[ channels[i] ]
                if (debug == 1):
                    a=int(sr_data)
                    # write data as a binary string, right adjusted, padded with zeros on the left
                    b=format(a, "b").rjust(31, '0')
                    print("sr_data: ", b)
                
        if(debug == 1):
            a=int(sr_data)
        # write data as a binary string, right adjusted, padded with zeros on the left
            b=format(a, "b").rjust(31, '0')
            print("sr_data: ", b)
            
        # add mux addresses.  this wouldn't work if channels[0] == 99.  In this case, it never is.
        # all four channels have the same address bits A0-A2, so just look at the first channel
        sr_data = sr_data | MUX[channels[0]]
        # invert selected channels
        sr_data_mod = sr_data ^ INVERT
        write_serial_register(ArduinoSerial, sr_data_mod )

    if (data == 'gnd'):
        ground_all_pads(ArduinoSerial)
        
    if (data == 's'):
        print("debug = ", debug)
        if (MODE == 0): print("\nVOLTAGE_MODE")
        if (MODE == 1): print("\nCURRENT_MODE")
        if (MODE == 2): print("\nCAL_MODE")
        print("gain resistor number: ", gain)
        print("channel: ", chan)
        print("group: ", group)
        print("channels: ", channels)
        a=int(sr_data)
        # write data as a binary string, right adjusted, padded with zeros on the left
        b=format(a, "b").rjust(31, '0')
        # split string up into smaller segments to improve readability
        c=b[0:5]
        d=b[5]
        e=b[6:11]
        f=b[11:16]
        g=b[16:21]
        h=b[21:26]
        i=b[26:31]
        print("sr_data: ",c, d, e, f, g, h, i)
        print("\n")

    if (data == 'h'):
        help()

    if (data == 'r'):
        # reset hardware and software.  what characteristics the reset state should have is still under consideration
        MODE = VOLTAGE_MODE
        if (debug == 1): print("sending reset")
        write_byte(ArduinoSerial, 5)
        #if (debug == 1): print("grounding pads")
        #ground_all_pads(ArduinoSerial)





        






