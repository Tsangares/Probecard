
# coding: utf-8
"""
Contains a MainMenu, with all of the configuaration variables defined.
The Gui class simple instantiates the MainMenu and handles window switching.
 - WCW 181127
"""
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import platform
if 'darwin' in platform.system().lower():
    import matplotlib
    matplotlib.use('TkAgg') #Mac support
    
import matplotlib.pyplot as plt

if __package__ in [None,""]:
    #Running from git clone
    from daq import *
    from menu import TwoPaneWindow
else:
    #Running from pip install
    from .daq import *
    from .menu import TwoPaneWindow



#Gui's in general have a lot of boiler plate code.
class Gui(QApplication):
    def __init__(self):
        super(Gui,self).__init__(['Probecardv1.4 DAQ'])

    def addMenu(self,menuWindow):
        self.menuWindow=menuWindow
        self.window = menuWindow
        self.window.onExperiment.connect(self.startExperiment)
        self.aboutToQuit.connect(self.window.exit)
        self.exec_()
    def startExperiment(self,msg):
        self.window.saveSettings()
        options = self.window.getData() #Menu options
        self.window.close()
        print("Settings pulled from menu: ",options)
        self.window=BasicDaqWindow(options) #QWindow
        if msg=='single':
            self.daq=SinglePixelDaq(options) #QThread
        elif msg == 'multi':
            self.daq = MultiPixelDaq(options)
        elif msg=='all':
            self.daq=AllPixelsDaq(options)
        elif msg=='calib':
            print(msg)
        else:
            print("error: wrong init.",msg)

        self.daq.newData.connect(self.window.addPoint)
        self.daq.done.connect(self.window.finalize)
        self.daq.log.connect(self.window.log)
        self.daq.start()
        
        self.window.done.connect(self.restore)
        self.window.stop.connect(self.daq.stop)
        self.window.show()
            
    def restore(self,msg):
        self.window = menuWindow
        self.window.show()
        #self.window.onExperiment.connect(self.startExperiment)
        self.aboutToQuit.connect(self.window.exit)


def five():
    return 6

if __name__ == "__main__":
    states={
        'single': 'Single Pixel',
        'multi': 'Multi Pixels',
        'all': 'Total Current',
        'calib': 'Calibration',
    }
    options=[
        ('Email', 'email','name@email.com'),
        ('Experiment Name (for excel)', 'filename','filename'),
        ('Plot Title', 'plotTitle','plotTitle'),
        ('Keithley Compliance (A)', 'kcomp'),
        ('Probecard controller COM port (#)',   'com'),
        ('Agilent Hold Time (sec)', 'holdTime'),
    ]
    gui=Gui()
    menuWindow=TwoPaneWindow(options,states)
    menuWindow.addStateWidget(states['multi'],(QLabel('Agilent Compliance (A)'),menuWindow.getLineEdit('acomp')))
    menuWindow.addStateWidget(states['single'],(QLabel('Channel Number (N)'),menuWindow.getLineEdit('channel_number')))
    menuWindow.loadAutosave()
    gui.addMenu(menuWindow)

