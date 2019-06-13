from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import platform
if 'darwin' in platform.system().lower():
    import matplotlib
    matplotlib.use('TkAgg') #Mac support

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import time
from threading import Thread
from multiprocessing import Process
from queue import Queue
from random import random
from abc import ABCMeta,abstractmethod
"""
This is supposed to be an abstract class,
that should be implemented by the child for the intended experiemt.
Currently the addPoint class is drastically too unique to be abstract.

TODO: Move addPoint to the inherited class.

A Detail Window had a log functionality & a scroll window for the log.
It also has a multi-subplot matplotlib canvas, and a custom menu section.
 - WCW 181127
"""

class DetailWindow(QMainWindow):
    __metaclass__=ABCMeta

    @abstractmethod
    def addPoint(self,point):
        """
        It is required to overwrite this funciton
        In this function add your data to the cache
        You can plot also or make a seperate function for plotting.
        Look at refresh in SinglePixelDaq.py for an example
        """
        
    def __init__(self):
        super(DetailWindow,self).__init__()
        self.output=None
        
        #-- Setup Figures --#
        self._cache={}
        self.figs=[]
        self.figure=plt.figure() #Pyplot
        self.canvas=FigureCanvas(self.figure) #QWidget
        self.fig=self.figure.add_subplot(1,1,1)
        
        #-- Build Window --#
        self.setCentralWidget(QSplitter())
        layout=QHBoxLayout(self.centralWidget())
        menu=QWidget()
        self.menuLayout=QFormLayout(menu)
        self.menuLayout.addRow(self.getOutputBox())
        layout.addWidget(self.canvas)
        layout.addWidget(menu)

    #Returns the cache in tuple format so its easier to loop
    def getCache(self):
        return self._cache.items()

    #If you really need the data from a specific channel use this:
    #Example: self['chan1']
    def __getitems__(self,key):
        return self._cache[key]

    #Clear the plot
    def clear(self):
        self.fig.clear()
        
    #Draw the plot
    def draw(self):
        self.canvas.draw()

    #Add value to the plotting cache
    def cache(self,key,value):
        keys=[key for key,values in self._cache.items()]
        if key in keys:
            self._cache[key].append(value)
        else:
            self._cache[key]=[value]

    #Write a line in the OutputBox
    def log(self,*args):
        text=""
        if len(args) == 1 and type(args[0]) == tuple: args=args[0]
        for arg in args: text+=" %s"%str(arg)
        self.output.insertRow(0,QLabel("%.02f"%(time.time()%10000)),QLabel(text))

    #Defines the scroll area used for logging.
    def getOutputBox(self):
        scroll=QScrollArea()
        output=QWidget()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(500)
        scroll.setMinimumWidth(400)
        scroll.setWidget(output)
        layout=QFormLayout(output)
        self.output=layout
        return scroll

