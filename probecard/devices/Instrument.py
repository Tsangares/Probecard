import visa
import statistics as stats
#This is used to connect to devices using gpib
#The Instrument class should be inherited into a device specific class (see Agilent4155C)
class Instrument:
    def __init__(self):
        self.inst=None
        self.measurements=[]
        self.history=[]

    def clearRecord(self):
        self.measurements=[]
        self.history=[]

    #Converts a list of [{'chan1': 22, 'chan2': 43},{'chan1': 232, 'chan2': 433}]
    #To {'chan1': [22,232], 'chan2': [43,433]}
    def getRecord(self):
        out={}
        for measurement in self.measurements:
            for chan,val in measurement.items():
                if out.get(chan,None) is None: out[chan]=[]
                if type(val) == list:
                    out[chan].append(stats.mean(val))
                else:
                    out[chan].append(val)   
        self.history.append(out)
        self.clearRecord()
        return out
    
    def getName(self,inst=None):
        if inst is None:
            if self.inst is not None:
                inst=self.inst
            else:
                raise(Exception("Called getName without an Instrument selected."))
        try:
            return str(inst.query('*IDN?')).lower()
        except Exception:
            print("failed to query device: ",self.inst)
            return ""


    def test(self):
        return "working"

    #Args is a list of args
    def connect(self,*args):
        rm=visa.ResourceManager()
        for device in rm.list_resources():
            self.inst=rm.open_resource(device)
            idn=self.getName(self.inst).lower()
            for arg in args:
                if not arg.lower() in idn:
                    self.inst=None
                    break
            if self.inst is not None: break;
        if self.inst is None:
            raise Exception("The device %s was not found."%' '.join(args))
        else:
            print("Connected to %s"%' '.join(args))
            return self.inst

    def reset(self):
        self.inst.write("*RST;")
