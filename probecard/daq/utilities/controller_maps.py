import array
    
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
