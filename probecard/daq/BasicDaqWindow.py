'''
This file is the most basic daq that plots some value against voltage.
There are 3 aspects to a daq.
 - QApplication - Needed for all QT applications
 - QWindow - Needed to display the data, log and buttons
 - QThread - Needed to gather data and emit data to plot on the QWindow
The QWindow is occupied with diplaying information to the user,
The QThread allows the user to interact with the QWindow concurrent to data taking & plotting.
We use pyqtSingal to transfer data between the QThread and QWindow,
 because the pyqtSginal will interupt the QWindow only momentarliy while it plotting,
 rather than the QWindow be fozen the total duration of data taking.
'''
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QLabel,QPushButton,QApplication
from random import random
from time import sleep,time
from io import BytesIO
if __package__ in [None,""]:
    from windows import DetailWindow
    from FinalizeDataThread import FinalizeDataThread
else:
    from .windows import DetailWindow
    from .FinalizeDataThread import FinalizeDataThread

class BasicDaqWindow(DetailWindow):
    done=pyqtSignal(str)
    def __init__(self,options):
        super(BasicDaqWindow,self).__init__()
        self.options=options
        self.volts=[]
        self.logy=options['logy']
        self.buildPlot()
        self.show()
        shutdown=QPushButton("Force Shutdown")
        self.menuLayout.addRow(shutdown)
        self.stop=shutdown.clicked
        self.stop.connect(lambda: self.log("Taking last round of data then shutting down."))
        toggle=QPushButton("Toggle y-axis log")
        self.menuLayout.addRow(toggle)
        self.setLogy=False
        toggle.clicked.connect(self.switchLogyToggle)
        self.start=time()
        
    def switchLogyToggle(self,msg):
        self.logy=not self.logy
        self.refresh()
        
    def buildPlot(self):
        #Setup the figure with x,y label and title.
        #self.fig.invert_xaxis()
        self.fig.legend()
        self.fig.invert_xaxis()
        if self.logy: self.fig.semilogy()
        self.fig.set_xlabel("Voltage (V)")
        self.fig.set_ylabel("Current (A)")
        if self.options['plotTitle'] == '':
            self.fig.set_title("Multichannel Current vs Voltage")
        else:
            self.fig.set_title(self.options['plotTitle'])

    #Input a voltage, current, on a given channel and plot it.
    #addPoint(float,float,string,bool)
    def addPoint(self,volt,value,chan,refresh=False):
        #Only unique/new voltages are added to the voltage list.
        if len(self.volts)==0 or self.volts[-1]!=volt:
            self.volts.append(volt)
        self.cache(chan,value)
        if refresh: self.refresh()
        
    def refresh(self,v=False):
        self.clear()
        if v: print(self.cache)
        for chan,values in self.getCache():
            if v: print(self.volts,values)
            volts=self.volts[:len(values)]
            self.fig.plot(volts,values,label=chan)
        self.buildPlot()
        self.draw()

    #Returns a dict of all the data in the plot
    def getData(self):
        output=self._cache.copy()
        output['voltage']=self.volts.copy()
        return output

    def getFigureData(self):
        imgdata = BytesIO()
        self.figure.savefig(imgdata, format='png')
        imgdata.seek(0)
        return imgdata.getbuffer()
    
    def finalize(self):
        print("Duration: %.02f secconds."%(time()-self.start))
        filename=self.options['filename']
        email=self.options['email']
        data=self.getData()
        figure=self.getFigureData()
        f=FinalizeDataThread(filename,email,data,figure)
        f.log.connect(self.log)
        f.done.connect(lambda: self.done.emit('done'))
        f.done.connect(lambda: self.close())
        sleep(1)
        f.run()
    

#EXAMPLE QThread        
class TestPlotting(QThread):
    newPoint=pyqtSignal(float,float,str,bool)
    def run(self):
        print("Generating points")
        for i in range(20):
            for j in range(4):
                #Generate some random data to plot
                self.newPoint.emit(i,random(),str(j),True)
                sleep(.2)
        
if __name__=='__main__':
    #If you run this file, it will run the test below.
    #-- Create basic GUI --#
    gui=QApplication(['test'])
    daq=BasicDaqWindow()
    gui.window=daq

    #-- Create a plotting thread --#
    test=TestPlotting()
    test.newPoint.connect(daq.addPoint)
    test.start()
    
    gui.exec_()
