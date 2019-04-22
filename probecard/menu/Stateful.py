from .Saveable import Saveable
from PyQt5.QtCore import pyqtSignal
"""
The purpose of Stateful is subtle.
There are commonly 4 experiments that use 90% of the same config parameters,
but each experiement is unique & had special parameters.
State can perserve the common parameters and create new, unique fields for specific experiments.
See addStateButton() in MenuWindow for more clarity.
"""
class Stateful(Saveable):
    onStateChange = pyqtSignal(str)
    def __init__(self):
        super(Stateful,self).__init__()
        self.state=None
        self.onLoad.connect(lambda: self.setState(self.getValue('state').text()))

    def getState(self):
        return self.state

    def setState(self,state):
        self.getValue('state').setText(state)
        self.state=state
        self.onStateChange.emit(state)
        return state
