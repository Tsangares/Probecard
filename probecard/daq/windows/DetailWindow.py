from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
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
    def __init__(self):
        super(DetailWindow,self).__init__()
        self.cache={}
        self.figs=[]
        self.output=None
        canvas,figure = self.getCanvas()
        self.figure=figure #Pyplot
        self.canvas=canvas #QWidget

        self.mainWidget=QSplitter()
        self.setCentralWidget(self.mainWidget)
        layout=QHBoxLayout(self.mainWidget)
        menu,menuLayout=self.getMenu()
        self.menuLayout=menuLayout
        layout.addWidget(menu)        
        layout.addWidget(canvas)
            
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

    def getMenu(self):
        menu=QWidget()
        layout=QFormLayout(menu)
        layout.addRow(self.getOutputBox())
        return menu,layout
        
    def getCanvas(self):
        figure=plt.figure()
        canvas=FigureCanvas(figure)
        self.testJumple()
        return canvas,figure
            
    def log(self,*args):
        text=""
        if len(args) == 1 and type(args[0]) == tuple: args=args[0]
        for arg in args: text+=" %s"%str(arg)
        self.output.insertRow(0,QLabel("%.02f"%(time.time()%10000)),QLabel(text))

    #All on one plot.
        #Assuming a point is of the form (float,key:float)
    @abstractmethod
    def addPoint(self,point):
        """Use point to plot into self.fig"""

    def clearPlot(self,msg=None):
        self.cache={}

    def testJumple(self):
        for fig in self.figs:
            fig.plot([x for x in range(100)],[random() for y in range(100)])
        
