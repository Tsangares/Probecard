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
    from menu import MenuWindow
else:
    #Running from pip install
    from .daq import MultiPixelDaq as Daq
    from .menu import MenuWindow

    
    

class MainMenu(MenuWindow):
    onExperiment = pyqtSignal(str)
    STATES={
        'single': 'Single Pixel',
        'many': 'Many Pixels',
        'unique': 'Unique Mode',
        'grounded': 'Grounded Mode',
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
        self.addStateButton(self.STATES['single'],'haa',lambda: print("apple"))
        self.addStateWidget(self.STATES['single'],QLabel("HAAAA"))
        
        self.addToolBar(self.toolbar)

        self.menu=menu

        btn=self.getToggle("debug")
        self.menu.layout().addRow(QLabel("Debug Mode"),btn)
        self.menu.layout().addRow(self.stateWidget)

        self.buildRegionButtons(self.rightLayout)#Big setup function
        
        self.loadAutosave()
        self.show()

    def buildRegionButtons(self,layout):
        self.regionsLayout=layout
        self.addRegionBtn=QPushButton('Add Region')
        self.delRegionBtn=QPushButton('Delete Region')
        layout.addRow(self.delRegionBtn,self.addRegionBtn)
        self.addRegionBtn.clicked.connect(self.addRegion)
        self.delRegionBtn.clicked.connect(self.delRegion)
        self.regions=[]
        self.recoverRegions()
        
    def recoverRegions(self):
        settings=self.getSettings()
        if settings is None: return
        regions = [ key for key,value in settings.items() if 'region' in key  and 'start' in key ]
        for region in range(len(regions)):
            self.addRegion()
        
        
    def addRegion(self,msg=None):
        layout=self.regionsLayout
        key='region_%s'%len(self.regions)
        labels=self.getLabelFromKey(key)
        dbkeys=self.getDbKeyFromKey(key)
        startBtn=self.getLineEdit(dbkeys['start'])
        if len(self.regions) >= 1:
            prevKey='region_%s'%(len(self.regions)-1)
            prevEndButton=self.database[self.getDbKeyFromKey(prevKey)['end']]
            startBtn.setReadOnly(True)
            startBtn.setStyleSheet('background-color:#eee;color:gray')
            prevEndButton.editingFinished.connect(lambda: startBtn.setText(prevEndButton.text()))
            startBtn.setText(prevEndButton.text())
        self.regions.append(key)
        endBtn=self.getLineEdit(dbkeys['end'])
        stepsBtn=self.getLineEdit(dbkeys['steps'])
        endBtn.setText("0")
        stepsBtn.setText("0")
        layout.addRow(QLabel(labels['start']), startBtn)
        layout.addRow(QLabel(labels['end']), endBtn)
        layout.addRow(QLabel(labels['steps']), stepsBtn)

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
        if len(self.regions) == 1: return
        key=self.regions[-1]
        self.regions.remove(key)
        labels=self.getLabelFromKey(key)
        for k,label in labels.items():
            self.removeWidget(self.regionsLayout, QLabel, label)
        dbkeys=self.getDbKeyFromKey(key)
        for k,dbkey in dbkeys.items():
            self.delete(dbkey)
    
    #Sourcing voltage to zero and reading current on the Agilent
    #Keithly is used to source voltage set by these options
    def getCurrentSetup(self):
        options=[
            {'name': 'Email', 'key': 'email'},
            {'name': 'Experiment Name (for excel)', 'key': 'filename'},
            {'name': 'Keithley Compliance (A)',    'key': 'kcomp'},
            {'name': 'Agilent Compliance for All Chans (V)', 'key': 'acomp'},
            {'name': 'Resistance (Ohms)', 'key': 'resistance'},
            {'name': 'Arduino COM port number',   'key': 'com'},
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
