// version 4 02/28/18 works with Python script "Write_HPK-5x5_V7.0j.py"
#include<SPI.h>

// Define data's type
int data, i;
byte opcode;
byte ssr_data[4], ssr_copy[4], default_ssr_data[4];

// define modes
int MODE = 0;
int VOLTAGE_MODE = 0;
int CURRENT_MODE = 1;
int CAL_MODE = 2;
int DISABLE_MUX = 3;

// define opcodes
int SET_GAIN = 0;
int WRITE_SR = 1;
int SET_CURRENT_MODE = 2;
int SET_CAL_MODE = 3;
int SET_VOLTAGE_MODE = 4;
int RESET = 5;
int READ_SR = 6;
int SET_DISABLE_MUX = 7;
int NAME=8;

// assign Pro Micro pins
int EN = 2; // lower tier mux enable, active high
int EN2 = 8;  // enable for second tier multiplexer, active high
int OE = 19;   // serial to parallel output enable, active high
int LE = 18;  // serial to parallel latch enable, active high
// currrent to voltage converter gain resistor select
// normally only one select line to be high at a time.
// resistor values depend on what is loaded on pcb.  user can change.
int RS1 = 7;
int RS2 = 6;
int RS3 = 5;
int RS4 = 4;
int RS5 = 3;
byte gain = 5;
byte old_gain = 5;
int debug = 21;

void setup() {
   //initialize serial COM at 9600 baud rate
   Serial.begin(9600);
   SPI.begin();
   SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
   //output pins
   pinMode(EN, OUTPUT); // multiplexer enable
   pinMode(EN2, OUTPUT); // second tier multiplexer enable
   // serial to parallel converter control signals
   pinMode(OE, OUTPUT);  // output enable, active high
   pinMode(LE, OUTPUT);  // latch enable, active high
   // current to voltage converter gain control
   pinMode(RS1, OUTPUT);  // gain resistor #1 select
   pinMode(RS2, OUTPUT);  // gain resistor #2 select
   pinMode(RS3, OUTPUT);  // gain resistor #3 select
   pinMode(RS4, OUTPUT);  // gain resistor #4 select
   pinMode(RS5, OUTPUT);  // gain resistor #5 select
   pinMode(debug, OUTPUT);
   //set all analog swtiches to ground sensors.
   digitalWrite(OE, LOW); //forces all outputs low
   digitalWrite(LE, LOW);
   // load serial shift register with zeros or ones as needed to ground all pads
   // 2 outputs out of every 3 SPSD switches are reversed, rquiring select lines to be high to ground pads
   // the bit pattern below will ground all channels, and set all address bits low
   // note: serial data is transferred in order of byte 0, byte 1, byte2, byte 3.
   // save bit pattern to ground all pads for default state, and to ground on command (not implemented).
   default_ssr_data[3] = B10110111;
   default_ssr_data[2] = B01101101;
   default_ssr_data[1] = B11011011;
   default_ssr_data[0] = B00000010;
   // copy default pattern to working storage
   for (i = 0; i < 4; i++)
     ssr_data[i] = default_ssr_data[i];
   // SPI.transfer zeros out the array that is given as data, probably by shifting data out and padding with zeros.
   // so to preserve ssr_data, transfer a copy of it.
   for (i = 0; i < 4; i++)
     ssr_copy[i] = ssr_data[i];
   SPI.transfer(ssr_copy, 4);
   //transfer data to outputs
   digitalWrite(LE, HIGH);
   delay(100);
   digitalWrite(LE, LOW);
   digitalWrite(OE, HIGH);
   //default gain is at highest setting, 15M currently
   digitalWrite(RS1, LOW);
   digitalWrite(RS2, LOW);
   digitalWrite(RS3, LOW);
   digitalWrite(RS4, LOW);
   digitalWrite(RS5, HIGH);
   //multiplexer channels will be floating because all probes will be grounded. This should cause voltage
   // output of current to voltage converter to be close to ground.
   digitalWrite(EN, HIGH);
   digitalWrite(EN2, HIGH);
   digitalWrite(debug, LOW);
} // end setup

void loop() {
   // read in one byte of binary data from Python, which contains op code
   // Get Data - read one byte with op code and gain setting
   //  0 - select currrent to voltage converter feedback resistor (by number, not value)
   //  1 - write four bytes to serial shift register, setting input switches and mux addresses
   //  2 - select current mode - read out four channels at a time, as currents
   //  3 - select cal mode - disable first tier muxes, enable final mux, use current output as current input,
   //      to calibrate converter
   //  4 - select voltage readout mode - use all muxes to route currents to current to voltage converter
   //  5 - reset - not defined at this time
   //  6 - read back serial shift register data
   //  7 - disable all multiplexers.  possibly useful for measuring leakage currents in different parts
   //      of the system.  may also be useful when grounding all pads.

   while (!Serial.available()) {}; // wait for input.  this step is essential in order not to timeout and miss input.
   while (Serial.available()) {
     opcode = Serial.read();  // read one byte
     Serial.write(opcode); // write back for verification
     break;  // read one byte only, then decode to decide what else to do.
   } // end while
   
   if ( opcode == SET_GAIN) {
     // update gain of current to voltage converter
     while (!Serial.available()) {};  // wait for input
     while (Serial.available()) {
       gain = Serial.read(); // read one byte containing gain setting
       Serial.write(gain);  // write back to verify
       break;
     } // end while
     // for best results, turn on new resistor first, then turn off old resistor.
     // this prevents output of current to voltage circuit from drifting to rail voltage
     // if there is no feedback resistor in the circuit.
     // turn on new gain resistor
     //digitalWrite(debug, HIGH);
     if (gain == 1) digitalWrite(RS1, HIGH);
     if (gain == 2) digitalWrite(RS2, HIGH);
     if (gain == 3) digitalWrite(RS3, HIGH);
     if (gain == 4) digitalWrite(RS4, HIGH);
     if (gain == 5) digitalWrite(RS5, HIGH);
     // turn off old gain resistor
     if (old_gain == 1) digitalWrite(RS1, LOW);
     if (old_gain == 2) digitalWrite(RS2, LOW);
     if (old_gain == 3) digitalWrite(RS3, LOW);
     if (old_gain == 4) digitalWrite(RS4, LOW);
     if (old_gain == 5) digitalWrite(RS5, LOW);
     // save new gain setting
     old_gain = gain;
   } // end if opcode == SET_GAIN

   if ( opcode == WRITE_SR ) {
     //write four bytes to serial shift register
     digitalWrite(debug, HIGH);
     digitalWrite(EN, LOW);
     digitalWrite(EN2, LOW);
     while (!Serial.available()) {}; // wait for input
     while (Serial.available()) {
       //digitalWrite(debug, HIGH);
       Serial.readBytes(ssr_data, 4); // read four byte
       Serial.write(ssr_data, 4); // readback for verification
       // create a copy of the data, and transfer that to avoid distroying ssr_data.
       for (i = 0; i < 4; i++)
         ssr_copy[i] = ssr_data[i];
       SPI.transfer(ssr_copy, 4);    // transfer data to ssr.
       break;
     }
     digitalWrite(OE, LOW); // check data sheet for signal timing
     digitalWrite(LE, HIGH);  //clock data into transparent latches
     digitalWrite(LE, LOW);
     digitalWrite(OE, HIGH);  // maybe just leave it high?
     if ( MODE != CAL_MODE && MODE != DISABLE_MUX) {
       digitalWrite(EN, HIGH);
     }
     if ( MODE != CURRENT_MODE && MODE != DISABLE_MUX) {
       digitalWrite(EN2, HIGH);
     }
   }  // end if opcode == WRITE_SR

   if ( opcode == SET_CURRENT_MODE) {
     // disable second tier mux.  enable first tier muxes.  use current outputs.
     MODE = CURRENT_MODE;
     digitalWrite(EN, HIGH);
     digitalWrite(EN2, LOW);
   } // end if

   if ( opcode == SET_CAL_MODE) {
     // disable lower tier muxes.  enabel upper tier mux.  use current output as current 
     // input to current to voltage stage for calibration
     //digitalWrite(debug, HIGH);
     MODE = CAL_MODE;
     digitalWrite(EN, LOW);
     digitalWrite(EN2, HIGH);
     // A3 and A4 must be set to select the current output to use as an input.
     // these are set by serial to parallel shift reg, which must be programmed by the Python code.
   } // end if

   if (opcode == SET_VOLTAGE_MODE) {
     MODE = VOLTAGE_MODE;
     digitalWrite(EN, HIGH);
     digitalWrite(EN2, HIGH);
   }

   if (opcode == RESET) {
     digitalWrite(debug, LOW);
   }

   if (opcode == READ_SR) {
     //digitalWrite(debug, LOW);
     Serial.write(ssr_data, 4);
   }

   if (opcode == SET_DISABLE_MUX) {
     // disable multiplexers.  This is not strictly necessary, but may be useful for debugging, and
     // measuring leakage currents in different parts of the system.
     MODE = DISABLE_MUX;
     digitalWrite(EN, LOW);
     digitalWrite(EN2, LOW);
   }
   if (opcode == NAME){
     Serial.write("ProbecardV2 Controller ATmega32U4_5V_16MHz");
   }
} // end main loop
