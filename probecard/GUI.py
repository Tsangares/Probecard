# coding: utf-8
"""
Contains a MainMenu, with all of the configuaration variables defined.
The Gui class simple instantiates the MainMenu and handles window switching.
 - WCW 181127
"""
import time,threading,json
import platform as platform
import os.path
from multiprocessing import Process
from threading import Thread

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

try:
    import matplotlib.pyplot as plt
except:
    #Mac support
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


if __package__ in [None,""]:
    #Running from git clone
    from daq import MultiPixelDaq as Daq
    from menu import MenuWindow,RegionWindow
    from daq.utilities.controller_maps import Resistor
else:
    #Running from pip install
    from .daq import MultiPixelDaq as Daq
    from .menu import MenuWindow,RegionWindow
    from .daq.utilities.controller_maps import Resistor

    
    

class MainMenu(RegionWindow):
    onExperiment = pyqtSignal(str)
    STATES={
        'single': 'Single Pixel',
        'many': 'Many Pixels',
        'all': 'All Pixels',
        'calib': 'Calibration',
    }
    def __init__(self):
        #States need to be configured first to setup the toolbar
        
        states=[e[1] for e in self.STATES.items()]
        
        super(MainMenu,self).__init__(states)

        #Rename getWidget to generateMenuBaseOnJsonOptions
        menu=self.getWidget(self.getCurrentSetup(), action=self.initDuo)
        
        self.rightPane=QWidget()
        self.splitter=QSplitter()
        layout=QHBoxLayout(self.splitter)
        layout.addWidget(menu)
        layout.addWidget(self.rightPane)
        self.rightLayout=QFormLayout(self.rightPane)
        
        self.setCentralWidget(self.splitter)
        #Create state buttons

        
        self.addToolBar(self.toolbar)

        self.menu=menu

        btn=self.getToggle("debug")
        self.menu.layout().addRow(QLabel("Debug Mode"),btn)
        self.menu.layout().addRow(self.stateWidget)
        
        self.buildRegionButtons(self.rightLayout)#Big setup function
        self.buildStates()
        
        self.loadAutosave()
        self.show()

    def buildStates(self):
        #Single Mode
        resistance=self.getComboBox('resistance')
        for label in Resistor.labels: resistance.addItem(label)
        self.addStateWidget(self.STATES['single'],(QLabel("Resistance (ohm)"),resistance))
        
        #Many Mode


        #All Mode
        
        self.addStateButton(self.STATES['many'],'haa',lambda: print("apple"))
        self.addStateWidget(self.STATES['many'],QLabel("HAAAA"))

    
    #Sourcing voltage to zero and reading current on the Agilent
    #Keithly is used to source voltage set by these options
    def getCurrentSetup(self):
        options=[
            {'name': 'Email', 'key': 'email'},
            {'name': 'Experiment Name (for excel)', 'key': 'filename'},
            {'name': 'Keithley Compliance (A)',    'key': 'kcomp'},
            {'name': 'Agilent Compliance for All Chans (V)', 'key': 'acomp'},
            {'name': 'Probecard controller COM port (#)',   'key': 'com'},
            {'name': 'Agilent Hold Time (sec)',      'key': 'holdTime'},
        ]
        return options
    
    #Connects gui to the experiments code.
    def initDuo(self):
        self.statusBar().showMessage("Started Duo!", 2000)
        self.onExperiment.emit("init")

#Gui's in general have a lot of boiler plate code.
class Gui(QApplication):

    def __init__(self):
        super(Gui,self).__init__(['Multi-Channel DAQ'])
        self.window = MainMenu()
        self.window.onExperiment.connect(self.startExperiment)
        self.aboutToQuit.connect(self.window.exit)
        self.exec_()
        
    def startExperiment(self,msg):
        if(msg == 'init'):
            self.window.saveSettings()
            data = self.window.getData()
            self.window.close()
            self.window = Daq(data)
            self.window.onFinish.connect(self.restore)
    def restore(self,msg):
        self.window = MainMenu()
        self.window.onExperiment.connect(self.startExperiment)
        self.aboutToQuit.connect(self.window.exit)

def init():
    gui=Gui()

def five():
    return 6

if __name__ == "__main__":
    init()
