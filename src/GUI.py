# coding: utf-8
"""
Contains a MainMenu, with all of the configuaration variables defined.
The Gui class simple instantiates the MainMenu and handles window switching.
 - WCW 181127
"""
import time,threading
import platform as platform
import json
import os.path

from Agilent import AgilentE4980a, Agilent4156
from PowerSupply import PowerSupplyFactory

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from multiprocessing import Process
from threading import Thread
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from Core import MenuWindow
from DetailWindow import DetailWindow
from MultiChannelDaq import MultiChannelDaq as Daq


class MainMenu(MenuWindow):
    onExperiment = pyqtSignal(str)
    def __init__(self):
        #States need to be configured first to setup the toolbar
        states=['Read Current', 'Read Voltage']
        super(MainMenu,self).__init__(states)

        #This setups the fields and buttons

        #Rename getWidget to generateMenuBaseOnJsonOptions
        menu=self.getWidget(self.getCurrentSetup(), action=self.initDuo)
        self.setCentralWidget(menu)
        self.menu=menu
        self.menu.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        #This will change the page when the toolbar is perturbed.
        self.addRegionBtn=QPushButton('Add Region')
        self.delRegionBtn=QPushButton('Delete Region')
        menu.layout().addRow(self.delRegionBtn,self.addRegionBtn)
        self.addRegionBtn.clicked.connect(self.addRegion)
        self.delRegionBtn.clicked.connect(self.delRegion)
        self.regions=[]
        self.recoverRegions()
        self.loadAutosave()
        self.show()

    def test(self):
        print("pressed")

    def recoverRegions(self):
        settings=self.getSettings()
        regions = [ key for key,value in settings.items() if 'region' in key  and 'start' in key ]
        for region in range(len(regions)):
            self.addRegion()
        
        
    def addRegion(self,msg=None):
        key='region_%s'%len(self.regions)
        labels=self.getLabelFromKey(key)
        dbkeys=self.getDbKeyFromKey(key)
        self.regions.append(key)
        self.menu.layout().addRow(QLabel(labels['start']), self.getLineEdit(dbkeys['start']))
        self.menu.layout().addRow(QLabel(labels['end']), self.getLineEdit(dbkeys['end']))
        self.menu.layout().addRow(QLabel(labels['steps']), self.getLineEdit(dbkeys['steps']))

    def getLabelFromKey(self,key):
        return {
            'start': key+" Start (V)",
            'end': key+" End (V)",
            'steps': key+" Steps (#)",
        }
    def getDbKeyFromKey(self,key):
        return {
            'start': key+'_start',
            'end': key+'_end',
            'steps': key+'_steps',
        }
            
    
    def delRegion(self,msg=None):
        if len(self.regions) == 0: return
        key=self.regions[-1]
        self.regions.remove(key)
        labels=self.getLabelFromKey(key)
        for k,label in labels.items():
            self.removeWidget(self.menu, QLabel, label)
        dbkeys=self.getDbKeyFromKey(key)
        for k,dbkey in dbkeys.items():
            self.delete(dbkey)


    
    #Sourcing voltage to zero and reading current on the Agilent
    #Keithly is used to source voltage set by these options
    def getCurrentSetup(self):
        options=[
            {'name': 'Email', 'key': 'email'},
            {'name': 'Filename', 'key': 'filename'},
            {'name': 'Keithley Compliance (A)',    'key': 'kcomp'},
            {'name': 'Agilent Hold Time (sec)',      'key': 'holdTime'},
            {'name': 'Agilent Measurement Delay (sec)',  'key': 'measDelay'},
            {'name': 'Agilent Measurement Time (sec)',   'key': 'measTime'},
            {'name': 'Arduino COM port number',   'key': 'com'},
            {'name': 'Average value over N samples', 'key': 'repeat'},
            {'name': 'Resistance (Ohms)', 'key': 'resistance'},
            {'name': 'Agilent Compliance for All Chans (V)', 'key': 'acomp'}
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
        
gui=Gui()

