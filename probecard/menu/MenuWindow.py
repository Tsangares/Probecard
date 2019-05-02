from .StateWindow import StateWindow
from .ValueHandler import *
from .Saveable import Saveable
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#Makes a menu of label-lineedits with a start button
class MenuWindow(Saveable):
    #Converts a dict of <name,key> objects to a form.
    #The `name` is a human readable descriptior,
    # and `key` pulls options from the gui to give to the experiment's code
    def getMenuLayout(self,options):
        layout = QFormLayout()
        keys=self.getKeys()
        for opt in options:
            key=opt['key']
            if key in keys:
                print("Handling a duplicate key, %s"%key)
                layout.addRow(QLabel(opt['name']),self[key])
            else:
                layout.addRow(QLabel(opt['name']),self.getLineEdit(key))
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(5)
        return layout

    #Generates the fields based on options and sets up the standard buttons.
    def getMenuWidget(self,options,action=None,name=None):
        widget = QWidget()
        widget.setAccessibleName(name)
        
        #Get options
        layout=self.getMenuLayout(options)
        widget.setLayout(layout)
        
        #Setup buttons
        startBtn=QPushButton('Start')
        if action != None: startBtn.clicked.connect(action)
        layout.addRow(startBtn)
        
        return widget
                
