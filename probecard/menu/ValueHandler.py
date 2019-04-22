from PyQt5.QtCore import *
from PyQt5.QtWidgets import QLineEdit,QCheckBox
#Value Handler simplifies getting the data from the input fields on the gui.
class ValueHandler:
    def __init__(self):
        self.database={}
    def getSpinBox(self,label):
        self.database[label] = QSpinBox()
        return self.database[label]
    def getLineEdit(self,label):
        self.database[label] = QLineEdit()
        return self.database[label]
    def getToggle(self,label):
        self.database[label] = QCheckBox()
        return self.database[label]
    def getValue(self, key):
        return self.database[key]
    def getData(self):
        output={}
        for key,data in self.database.items():
            if(type(data) == QCheckBox):
                output[key]=data.checkState()
            else:
                output[key]=data.text()
        return output
    def delete(self, key):
        return self.database.pop(key,None)
    def dump(self):
        print(self.getData())

