from abc import ABC,abstractmethod
from .StateWindow import StateWindow
from .RegionWindow import RegionWindow
from .MenuWidget import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class TwoPaneWindow(StateWindow,RegionWindow):
    onExperiment = pyqtSignal(str)
    def __init__(self,options,states):
        super(TwoPaneWindow,self).__init__()
        self.statesMap=states
        self.options=options

        #-- Build general layout --#
        self.setCentralWidget(QSplitter())
        layout=QHBoxLayout(self.centralWidget())

        #rightPane is a widget vertially laid out in a form.
        getState=lambda: self.onExperiment.emit(_states[self.getState()])
        leftPane=MenuActionWidget(self.options, self, action=getState, action_text='Start Aquiring Data')
        self.centralWidget().layout().addWidget(leftPane)


        #rightPane is a widget vertially laid out in a form.
        rightWidget=QWidget()
        rightPane=QFormLayout(rightWidget).parentWidget()
        self.centralWidget().layout().addWidget(rightPane)

        #-- StateWindow Config --#
        for state,name in self.statesMap.items(): self.addState(name)
        self.addToolBar(self.toolbar)#Add State toolbar
        
        #-- RegionWindow Config --#
        self.buildRegionButtons(rightPane.layout())#Big setup function

        #-- Logy toggle --#
        logy=self.getToggle("logy")
        leftPane.layout().addRow(QLabel("Logarithmic Y-Axis"),logy)

        #-- DEBUG --#
        btn=self.getToggle("debug")
        leftPane.layout().addRow(QLabel("Debug Mode"),btn)
        leftPane.layout().addRow(self.stateWidget)

        _states={data:key for key,data in self.statesMap.items()}


        #-- Save Setup --#
        self.loadAutosave()
        self.show()
