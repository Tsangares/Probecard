from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from abc import ABCMeta,abstractmethod

class ValueObject():
    __metaclass__=ABCMeta
    @abstractmethod
    def getValue(self):
        '''Must return the data in the unique way the widget requires'''
    @abstractmethod
    def setValue(self):
        '''Must set the states of the object from the save file'''
        
class LineEdit(QLineEdit,ValueObject):
    def getValue(self):
        return self.text()
    def setValue(self,value):
        return self.setText(value)
class SpinBox(QSpinBox,ValueObject):
    def getValue(self):
        return self.text()
    def setValue(self,value):
        return self.setText(value)
class CheckBox(QCheckBox,ValueObject):
    def getValue(self):
        return self.checkState()==2
    def setValue(self,value):
        if issubclass(type(value),bool):
            if value: value=2
            else: value=0
        return self.setCheckState(value)
class ComboBox(QComboBox,ValueObject):
    def getValue(self):
        return self.currentText()
    def setValue(self,value):
        return self.setCurrentText(value)
    
#Value Handler simplifies getting the data from the input fields on the gui.    
class ValueHandler:
    def __init__(self):
        self._database={}
        
    def __setitem__(self,key,value):
        if not issubclass(type(value),ValueObject):
            raise(Exception("Object must inherit ValueObject."))
        else: self._database[key]=value
        return value
    def __getitem__(self,key):
        return self._database[key]

    def items(self):
        return self._database.items()

    def getKeys(self):
        return [key for key,item in self.items()]
    
    #Add just makes making the helper functions one-liners
    def add(self,key,value):
        self[key]=value
        return value

    #These are just helper functions to make adding a saveable QWidget easier
    def getSpinBox(self,label):
        return self.add(label,SpinBox())
    def getLineEdit(self,label,default=None):
        return self.add(label,LineEdit(default))
    def getComboBox(self,label):
        return self.add(label,ComboBox())
    def getToggle(self,label):
        return self.add(label,CheckBox())
    def getKeys(self):
        return [key for key,data in self._database.items()]
    #Returns all of the data contained the database
    def getData(self):
        return {key: data.getValue() for key,data in self.items()}
    def delete(self, key):
        return self._database.pop(key,None)
    def dump(self):
        print(self.getData())

