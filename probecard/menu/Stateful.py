
from PyQt5.QtCore import pyqtSignal
"""
The purpose of Stateful is subtle.
There are commonly 4 experiments that use 90% of the same config parameters,
but each experiement is unique & had special parameters.
State can perserve the common parameters and create new, unique fields for specific experiments.
See addStateButton() in MenuWindow for more clarity.
"""
