import time, visa
from Instrument import Instrument
#_rm=visa.ResourceManager()
class Agilent4156(object):

    def __init__(self, gpib=2):
        """Set up gpib controller for device"""

        assert(gpib >= 0), "Please enter a valid GPIB address"
        self.gpib_addr = gpib

        print("Initializing Agilent semiconductor parameter analyzer")
        rm = visa.ResourceManager()
        self.inst = rm.list_resources()[0]
        for x in rm.list_resources():
            if str(self.gpib_addr) in x:
                print("Found agilent lcrmeter")
                self.inst = rm.open_resource(x)

        self.inst = rm.open_resource(rm.list_resources()[0])
        print(self.inst.query("*IDN?"))

        self.inst.write("*RST")
        self.inst.write("*ESE 60;*SRE 48;*CLS;")
        self.inst.timeout = 10000

    def configure_measurement(self, _mode=1):
        mode = {0:":PAGE:CHAN:MODE SWE;", 1:":PAGE:CHAN:MODE SAMP", 2:":PAGE:CHAN:MODE QSCV"}.get(
             _mode, ":PAGE:CHAN:MODE SAMP")

        self.inst.write(mode)

    def configure_sampling_measurement(self, _mode=0, _filter=False, auto_time=True,
                                       hold_time=0, interval=4e-3, total_time=0.4, no_samples=10):
        mode = {0:"LIN", 1:"L10", 2:"L25", 3:"L50", 4:"THIN"}.get(_mode, "LIN")
        self.inst.write(":PAGE:MEAS:SAMP:MODE " + mode + ";")
        self.inst.write(":PAGE:MEAS:SAMP:HTIM " + str(hold_time) + ";")
        self.inst.write(":PAGE:MEAS:SAMP:IINT " + str(interval) + ";")
        if _filter is True:
            self.inst.write(":PAGE:MEAS:SAMP:FILT ON;")
        else:
            self.inst.write(":PAGE:MEAS:SAMP:FILT OFF;")

        self.inst.write(":PAGE:MEAS:SAMP:PER " + str(total_time) + ";")
        if auto_time is True:
            self.inst.write(":PAGE:MEAS:SAMP:PER:AUTO ON;")
        else:
            self.inst.write(":PAGE:MEAS:SAMP:PER:AUTO OFF;")

        self.inst.write(":PAGE:MEAS:SAMP:POIN " + str(no_samples) + ";")

    def configure_sampling_stop(self, stop_condition=False, no_events=1,
                                 _event_type=0, delay=0, thresh=0, var="V2"):

        event_type = {0:"LOW", 1:"HIGH", 2:"ABSL", 3:"ABSH"}.get(_event_type, "LOW")
        if stop_condition is True:
            self.inst.write(":PAGE:MEAS:SAMP:SCON ON;")
        else:
            self.inst.write(":PAGE:MEAS:SAMP:SCON OFF;")

        self.inst.write(":PAGE:MEAS:SAMP:SCON:ECO " + str(no_events) + ";")
        self.inst.write(":PAGE:MEAS:SAMP:SCON:EDEL " + str(delay) + ";")
        self.inst.write(":PAGE:MEAS:SAMP:SCON:EVEN " + event_type + ";")
        self.inst.write(":PAGE:MEAS:SAMP:SCON:NAME \'" + var + "\';")
        self.inst.write(":PAGE:MEAS:SAMP:SCON:THR " + str(thresh) + ";")

    def measurement_actions(self, _action=2):

        action = {0:"APP", 1:"REP", 2:"SING", 3:"STOP"}.get(_action, "SING")
        self.inst.write(":PAGE:SCON:" + action + ";")

    def wait_for_acquisition(self):
        return self.inst.query("*OPC?")

    def read_trace_data(self, var="I1"):
        _data = self.inst.query(":FORM:BORD NORM;DATA ASC;:DATA? \'" + var + "\';")
        # print _data
        try:
            data = map(lambda x: float(x), _data.split(","))
            return sum(data) / len(data)
        except:
            pass

    def configure_vmu(self, discharge=True, _vmu=1, _mode=0, name="VMU1"):
        vmu = {1:"VMU1", 2:"VMU2"}.get(_vmu, "VMU1")
        mode = {0:"V", 1:"DVOLT"}.get(_mode, "V")
        self.inst.write(":PAGE:CHAN:" + vmu + ":MODE " + mode + ";s")
        if discharge is True:
            self.inst.write(":PAGE:CHAN:" + vmu + ":DCH ON;")
        else:
            self.inst.write(":PAGE:CHAN:" + vmu + ":DCH OFF;")
        self.inst.write(":PAGE:CHAN:" + vmu + ":VNAM \'" + name + "\';")
        print("vmuset good")


    def configure_channel(self, _chan=0, standby=False):
        _func = 3
        _mode = 4
        chan = {0:"SMU1", 1:"SMU2", 2:"SMU3", 3:"SMU4"}.get(_chan, "SMU1")
        func = {0:"VAR1", 1:"VAR2", 2:"VARD", 3:"CONS"}.get(_func, "CONS")
        mode = {0:"V", 1:"I", 2:"VPUL", 3:"IPUL", 4:"COMM"}.get(_mode, "COMM")
        self.inst.write(":PAGE:CHAN:" + chan + ":FUNC " + func + ";")
        iname = {0:"I1", 1:"I2", 2:"I3", 3:"I4"}.get(_chan)
        vname = {0:"V1", 1:"V2", 2:"V3", 3:"V4"}.get(_chan)
        self.inst.write(":PAGE:CHAN:" + chan + ":INAM \'" + iname + "\';")
        self.inst.write(":PAGE:CHAN:" + chan + ":MODE " + mode + ";")

        if standby is True:
            self.inst.write(":PAGE:CHAN:" + chan + ":STAN ON;")
        else:
            self.inst.write(":PAGE:CHAN:" + chan + ":STAN OFF;")

        self.inst.write(":PAGE:CHAN:" + chan + ":VNAM \'" + vname + "\';")

    def configure_integration_time(self, NPLC=16, _int_time=1, short_time=640e-6):
        int_time = {0:"SHOR", 1:"MED", 2:"LONG"}.get(_int_time, "MED")
        self.inst.write(":PAGE:MEAS:MSET:ITIME:LONG " + str(NPLC) + ";")
        self.inst.write(":PAGE:MEAS:MSET:ITIME " + int_time + ";")
        self.inst.write(":PAGE:MEAS:MSET:ITIME:SHOR " + str(short_time) + ";")

class AgilentE4980a(object):

    def __init__(self, gpib=19):
        """Set up gpib controller for device"""

        assert(gpib >= 0), "Please enter a valid gpib address"
        self.gpib_addr = gpib

        print("Initializing agilent lcr_meter")
        rm = visa.ResourceManager()
        self.inst = 0
        for x in rm.list_resources():
            if str(self.gpib_addr) in x:
                print("found")
                self.inst = rm.open_resource(x)

        print(self.inst.query("*IDN?;"))

        self.inst.write("*RST;")
        self.inst.write("*ESE 60;*SRE 48;*CLS;")
        self.inst.timeout = 10000

    def configure_measurement(self, _function="CPD", _impedance=3, autorange=True):

        function = {0:"CPD", 1:"CPQ", 2:"CPG", 3:"CPRP", 4:"CSD", 5:"CSQ", 6:"CSRS", 7:"LPD",
                 8:"LPQ", 9:"LPG", 10:"LPRP", 11:"LPRD", 12:"LSD", 13:"LSQ", 14:"LSRS", 15:"LSRD",
                 16:"RX", 17:"ZTD", 18:"ZTR", 19:"GB", 20:"YTD", 21:"YTR", 22:"VDID"
                 }.get(_function, "CPRP")

        impedance = {0:"1E-1;", 1:"1E+0;", 2:"1E+1;", 3:"1E+2;", 4:"3E+2;", 5:"1E+3;", 6:"3E+3;", 7:"1E+4",
                     8:"3E+4", 9:"1E+5"}.get(_impedance, "1E+2")

        if autorange is True:
            self.inst.write(":FUNC:IMP " + _function + ";:FUNC:IMP:RANG:AUTO ON")
        else:
            self.inst.write(":FUNC:IMP " + _function + ";:FUNC:IMP:RANG: " + impedance)

    def configure_measurement_signal(self, frequency=10000, _signal_type=0, signal_level=5.0):
        signal_type = {0:"VOLT", 1:"CURR"}.get(_signal_type, "VOLT")
        self.inst.write(":FREQ " + str(float(frequency)) + ";:" + signal_type + " " + str(float(signal_level)))

    def configure_aperture(self, _meas_time, avg_factor=1):
        meas_time = {0:"SHOR", 1:"MED", 2:"LONG"}.get(_meas_time, "MED")
        self.inst.write(":APER " + meas_time + "," + str(float(avg_factor)) + ";")

    def initiate(self):
        self.inst.write(":INIT;")

    def __fetch_data(self):
        print("Pausing for 1 sec while machiene initializes.")
        time.sleep(1)
        _data_out = self.inst.query(":FETC?")
        # print _data_out
        data_out = _data_out
        parameter1 = data_out.split(",")[0]
        parameter2 = data_out.split(",")[1]

        results = (float(parameter1), float(parameter2))
        # print results
        return results

    def read_data(self):
        self.initiate()
        return self.__fetch_data()



# Agilent 4155C is a parameter analizer that has 4 voltage outputs and 4 inputs.
# I am not going to implement varaible voltage.
# I am only going to implement a constnant (zero) voltage and measuring the current.
class Agilent4155C(Instrument):
    def __init__(self, reset=False,connect=True):
        super(Agilent4155C,self).__init__()
        self.loc=None # Current Page
        self.mode=None # Sampling or Sweeping
        self.prefix=None # More speci`fic than a page, current selected field
        self.inputs=[]
        self.outputs=[]
        if connect is True: self.connect("4155c")
        if reset is True: self.reset()

    # query() and write() are helper functions
    # The intention is just to shorten and abstract form the instrument object.
    def query(self,command):
        return self.inst.query(command)

    def write(self,command):
        return self.inst.write(command)

    def reset(self):
        self.write("*RST;")
        print("Reset config.")

    # Prefix is a helper variable and functions.
    # The goal of prefix is to prefix every gpib command
    #  with the input field that is of interest.
    def setPrefix(self, prefix):
        self.prefix=prefix

    def getPrefix(self):
        return self.prefix

    def prefixWrite(self,command):
        if self.prefix is not None:
            self.write("%s:%s"%(self.prefix,command))
        else:
            raise Exception("Tried to write without a prefix. Set prefix with setPrefix function.")

    # getName() returns the name of the selected device.
    #def getName(self):
    #    return self.write("*IDN?")

    def run(self):
        return self.write(":PAGE:SCON:SING")

    # selectPage is a helper function
    # Lets you change the screen on the device
    # It also keeps track of the page it is on in the self.loc variable.
    def selectPage(self, page):
        self.loc=page
        return self.write(":PAGE:%s"%page)

    # Goto measureing page
    def selectMeasure(self):
        return self.selectPage("MEAS:"%self.mode)

    # Goto the channels page
    def selectChannels(self):
        return self.selectPage("CHAN")

    # Set Sweep vs Sampling mode and keep track of it.
    def setMode(self, mode):
        self.mode=mode
        return self.write(":PAGE:CHAN:MODE %s"%mode)
    def setSamplingMode(self):
        return self.setMode("SAMPling")
    def setSweepMode(self):
        return self.setMode("SWEep")


    # Setting integration
    def setIntTime(self, mode):
        self.integration=mode
        return self.write(":PAGE:MEAS:MSET:ITIM:MODE %s"%mode)
    def setLong(self):
        return self.setIntTime("LONG")
    def setMedium(self):
        return self.setIntTime("MED")
    def setShort(self):
        return self.setIntTime("SHOR")
    
    def setHoldTime(self, time):
        self.write(":PAGE:MEAS:%s:HTIMe %s"%(self.mode,time))

    def testSampleMode(self):
        if self.mode is None or "SAMP" not in self.mode.upper():
            print("Attempt to set sampling setting while not in sampling mode.")
            print("Switching to sampling mode...")
            self.setSamplingMode()

    # For sampling mode
    def setSampleSize(self, size):
        self.testSampleMode() #Warn user if the mode is not set correctly
        return self.write(":PAGE:MEAS:SAMP:POIN %s"%size)

    # This is the duration of each measurement.
    def setSampleDuration(self, duration):
        self.testSampleMode() #Warm user if the mode is not set correctly
        return self.write(":PAGE:MEAS:SAMP:PER %s"%duration)

    # Set a channel to a constant voltage
    # We want it at zero to measure current
    def setVoltage(self, channel, voltage, compliance):
        if int(channel)<0 or int(channel)>5:
            raise Exception("Channel is outside bounds. [1-4]; Given %s"%channel)

        #Configuring the channel
        self.setPrefix(":PAGE:CHAN:SMU%s"%channel) #Select SMU channel
        self.prefixWrite("MODE V") #Set to source voltage
        self.prefixWrite("FUNC CONS") #Set to constant
        self.prefixWrite("STAN OFF") #Disable standby

        #Configuring the measurement
        self.setPrefix(":PAGE:MEAS:%s:CONS:SMU%s"%(self.mode,channel))
        self.prefixWrite("SOURce %s"%voltage) #in 100mA
        if compliance > .1:
            print("Compliance too high, must be below 100 mA")
        else:
            self.prefixWrite("COMPliance %.10f"%compliance)
        print("Set voltage to %sV and compliance to %.10fA on Agilent's channel %s."%(voltage,compliance,channel))

        #Add to variable lists
        inputName="V%s"%channel
        outputName="I%s"%channel
        if inputName not in self.inputs:
            self.inputs.append(inputName)
        if outputName not in self.outputs:
            self.outputs.append(outputName)
        self.write(":PAGE:GLIS:LIST")

    # Set a channel to a constant current
    # We want it at zero to measure voltage
    def setCurrent(self, channel, current, compliance):
        if int(channel)<0 or int(channel)>5:
            raise Exception("Channel is outside bounds. [1-4]; Given %s"%channel)

        #Configuring the channel
        self.setPrefix(":PAGE:CHAN:SMU%s"%channel) #Select SMU channel
        self.prefixWrite("MODE I") #Set to source voltage
        self.prefixWrite("FUNC CONS") #Set to constant
        self.prefixWrite("STAN OFF") #Disable standby

        #Configuring the measurement
        self.setPrefix(":PAGE:MEAS:%s:CONS:SMU%s"%(self.mode,channel))
        self.prefixWrite("SOURce %s"%current) #in 100mA
        if abs(compliance) > 100:
            print("Compliance too big, must be below 100 V, above -100V")
        else:
            self.prefixWrite("COMPliance %.10f"%compliance)
        print("Set current to %sA and compliance to %.10fV on Agilent's channel %s."%(current,compliance,channel))

        #Add to variable lists
        inputName="I%s"%channel
        outputName="V%s"%channel
        if inputName not in self.inputs:
            self.inputs.append(inputName)
        if outputName not in self.outputs:
            self.outputs.append(outputName)
        self.write(":PAGE:GLIS:LIST")


    # Sets output data to ascii instead of binary
    def setOutputReadable(self):
        self.write(":FORM:BORD NORM; DATA ASC;")

    def getResults(self):
        results={}
        if len(self.outputs) == 1:
            return float(self.query(":DATA? '%s'"%self.outputs[0]))
        #This is a wierd statement. The variables have to be in the self.outputs list to be read.
        for output in self.outputs:
            results[output]=[float(val) for val in self.query(":DATA? '%s'"%output).split(',')]
        return results

    def prepareMeasurement(self):
        self.setPrefix(":PAGE:DISP")
        params=""
        for output in self.outputs:
            params+=", '%s'"%output
        self.prefixWrite("LIST '@TIME'%s"%params)

    def read(self, samples=None, duration=None):
        if samples is not None: self.setSampleSize(samples)
        if duration is not None: self.setSampleDuration(duration)
        self.setOutputReadable()
        self.prepareMeasurement()
        self.run()
        try:
            self.query("*OPC?")
        except visa.VisaIOError:
            print("Agilent timed out when asked if operation is complete. Lower meas. time to remove this warning.")
        return self.getResults()
    
    def getCurrent(self, samples=None, duration=None):
        return self.read(samples,duration)

    def getVoltage(self, samples=None, duration=None):
        return self.read(samples,duration)

