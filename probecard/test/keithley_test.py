import unittest
from contraption.Agilent import *
from contraption.PowerSupply import *
from numpy import linspace,polyfit
from time import sleep
import matplotlib.pyplot as plt
import statistics as stats
from math import *

class TestStringMethods(unittest.TestCase):

    def test_keithley_stop(self):
        return
        keith=Keithley2657a()
        #keith.powerDownPSU()
        #keith.configure_measurement(1,0,1)
        
        #keith.set_current_range('m')
        #keith.set_voltage_range(0)
        #keith.set_output(0)
        
    def test_common(self):
        #return
        agilent=Agilent4155C(reset=True)
        agilent.setSamplingMode()
        agilent.setStandby(True)
        keith=Keithley2657a()
        voltages=linspace(0,12,12)
        keith.enable_output(out=True)
        keith.set_compliance(.014)
        keith.set_current_range(10000)
        keith.set_voltage_range(0)
        for i in range(1,5):
                agilent.setCommon(i)
                print("Set agilent chan %d"%i)
        resistances=[]
        def ping():
            keith.set_output(5)
            sleep(1)
            keith.record()
            agilent.record()
            currents=agilent.getRecord()
            keiths=keith.getRecord()
            #print(currents,keiths)
            keith.stop()
        def process(title="",index=1):
            for volt in voltages:
                keith.set_output(volt)
                sleep(.2)
                print("Voltage set to %.02f measured %.02f V with %.02f A"%(volt,keith.get_voltage(),keith.get_current()))
                keith.record()
                agilent.record(samples=2)
            currents=agilent.getRecord()
            keiths=keith.getRecord()
            print(keiths)
            plt.subplot(2,2,index)
            for chan,vals in currents.items():
                if abs(stats.stdev(vals)) < 10**-10: continue
                plt.plot(keiths['voltage'],vals,marker=".",linestyle="None",color='c')
                m,b=polyfit(keiths['voltage'],vals,1)
                resistances.append((title+chan+" agilent",-1/m))
                plt.plot(keiths['voltage'],[m*x+b for x in keiths['voltage']],color='b')
                plt.title("%s %s agilent %.02f Ω"%(title,chan,1/m))
            kcurrent=[-I for I in keiths['current']]
            plt.subplot(2,2,index+1)
            plt.plot(keiths['voltage'],kcurrent,marker=".",linestyle="None",color='g')
            m,b=polyfit(keiths['voltage'],kcurrent,1)
            resistances.append((title+chan+" keithley",1/m))
            plt.plot(keiths['voltage'],[m*x+b for x in keiths['voltage']],color='r')
            plt.title("%s %s keithley %.02f Ω"%(title,chan,-1/m))
            keith.powerDownPSU()
        process("COMMON ",1)
        
        agilent=Agilent4155C(reset=True)
        agilent.setStandby(True)
        agilent.setSamplingMode()
        for i in range(1,5):
                agilent.setVoltage(i,0,sqrt(250)/1000)
                print("Set agilent chan %d"%i)
        process("V=0; ",3)
        print(resistances)
        plt.show()
        keith.powerDownPSU()
if __name__ == '__main__':
    unittest.main()
