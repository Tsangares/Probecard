from .StateWindow import StateWindow
from .ValueHandler import *
from .Saveable import Saveable
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from random import *
class MenuFormLayout(QFormLayout):
    def __init__(self,entries,config):
        super(MenuFormLayout,self).__init__()
        for i,entry in enumerate(entries):
            if   len(entry)==2:
                entries[i]=(entry[0],entry[1],"")
            elif len(entry)!=3:
                raise Exception("Menu entries not set properly")
        for label,key,default in entries:
            if key in config.getKeys():
                lineEdit=config[key]
            else:
                lineEdit=config.getLineEdit(key)
            lineEdit.setPlaceholderText(default)
            self.addRow(QLabel(label),lineEdit)
        self.setContentsMargins(20,20,20,20)
        self.setSpacing(5)

            
#Makes a menu of label-lineedits with a start button
class MenuWidget(QWidget):
    #Converts a dict of <name,key> objects to a form.
    #The `name` is a human readable descriptior,
    # and `key` pulls options from the gui to give to the experiment's code

    def __init__(self,options,config,name=None):
        super(MenuWidget,self).__init__()
        self.setLayout(MenuFormLayout(options,config))
        self.setAccessibleName(name)


class MenuActionWidget(MenuWidget):
    def __init__(self,options,config,action,action_text="",name=None):
        super(MenuActionWidget,self).__init__(options,config,name)
        self.actionBtn=QPushButton(action_text)
        self.actionBtn.clicked.connect(action)
        self.layout().addRow(self.actionBtn)
                
