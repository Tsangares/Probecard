"""
This Core.py files contains several helpful classes,
in the context of the UI builder pyQt5.
TimeSensitive - Enables a simple time keeping & printing
ValueHandler - Makes getting data from a GUI's form easier.
Saveable - Allows the GUI to save & load from a .json file.
Stateful - Uses Qt events to simply keep track of a state variable (for page changes, this can be used to make reusable fields in a UI).
MenuWindow - Implements all of these classes into an abstract class to be used to a specific menu.
 - WCW 181127
"""


import time,json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class TimeSensitive:
    def __init__(self):
        self.startTime=None
        self.endTime=None
  
    def checkpoint(self,relative=True,v=True):
        if not self.startTime is None:
            self.endTime=time.time()
            if v: print("Time %.04f"%(self.endTime-self.startTime))
            if relative: self.startTime=self.endTime
            else: self.endTime=self.startTime
        else:
            self.startTime=time.time()
  

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
    def getValue(self, key):
        return self.database[key]
    def getData(self):
        output={}
        for key,data in self.database.items():
            output[key]=data.text()
        return output
    def delete(self, key):
        return self.database.pop(key,None)
    def dump(self):
        print(self.getData())

#Saveable UI, a way to handle the data in a UI
#Uses ValueHandler but does not inherit it.
class Saveable(QMainWindow,ValueHandler):
    onLoad = pyqtSignal(str)
    onSave = pyqtSignal(str)

    def saveSettings(self, filename=".settings.tmp.json"):
        saveData=json.dumps(self.getData())
        with open(filename, "w") as f:
            f.write(saveData)
        self.onSave.emit('saved')

    #Get state from recently loaded save and deal with it.
    def setState():
        pass

    def exit(self):
        self.saveSettings(filename=".settings.tmp.json")
    
    def loadSettings(self,filename=".settings.tmp.json"):
        data=None
        try:
            with open(filename) as f:
                data=json.loads(f.read())
                f.close()
            if data != None:
                for key,field in data.items():
                    try:
                        self.getValue(key).setText(data[key])
                    except KeyError:
                        print("Nothing saved for %s"%key)
                self.onLoad.emit("loaded")
        except json.decoder.JSONDecodeError:
            print("Save file is corrupted, please delete %s"%filename)            
        except FileNotFoundError:
            print("No settings file.")

    def getSettings(self,filename=".settings.tmp.json"):
        data=None
        try:
            with open(filename) as f:
                data=json.loads(f.read())
                f.close()
            if data != None:
                return data
        except json.decoder.JSONDecodeError:
            print("Save file is corrupted, please delete %s"%filename)            
        except FileNotFoundError:
            print("No settings file.")

    def loadAutosave(self):
        self.loadSettings(filename=".settings.tmp.json")

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


#Menu Window inherits Stateful <- Saveable <- QMainWindow & ValueHandler
# It is mainly suposed to be a QMainWindow object with functions
# that assist with creating a casual input fields and buttons.
# The stateful aspect is for coordinating similar but slightly different pages
# Saveable means it autosaves fields on exit.
# Valuehadler is essentially a database to make running the experiment easier.
# The tool bar is a set of radio buttons representing possible states.
class MenuWindow(Stateful):
    def __init__(self, states=[]):
        super(MenuWindow,self).__init__()
        self.states=states
        self.toolbar = QToolBar()
        #self.addToolBar(self.toolbar)
        self.buildToolBar()

    #Call refreshToolbar when the state changes.
    def setState(self,state):
        self.refreshToolbar(state)
        return super(MenuWindow,self).setState(state)
        

    #Tries to visually match a state with a toolbar option.
    def refreshToolbar(self,state):
        for btn in self.getToolbarButtons():
            if btn.text() == state:
                btn.toggle()
                
    #Finds and Retuns a list of QRadioButton objects
    # There objects represent different states.
    def getToolbarButtons(self):
        out=[]
        for child in self.toolbar.children():
            if type(child) == QWidget:
                for c in child.children():
                    if type(c) == QRadioButton:
                        out.append(c)
        return out

    #Toolbar is used to switch between main-widgets/experiments
    #This takes the variable, self.states
    def buildToolBar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        self.database['state']=QLineEdit()
        for state in self.states:
            btn=QRadioButton(state)
            btn.clicked.connect(lambda a=True,b=btn: self.setState(b.text()))
            layout.addWidget(btn)
        self.toolbar.addWidget(widget)


    #Converts a dict of <name,key> objects to a form.
    #The `name` is a human readable descriptior,
    # and `key` pulls options from the gui to give to the experiment's code
    def getLayout(self,options):
        layout = QFormLayout()
        keys=[key for key,item in self.database.items()]
        for opt in options:
            key=opt['key']
            if key in keys:
                print("Handling a duplicate key, %s"%key)
                layout.addRow(QLabel(opt['name']),self.getValue(key))
            else:
                layout.addRow(QLabel(opt['name']),self.getLineEdit(key))
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(5)
        return layout

    #Generates the fields based on options and sets up the standard buttons.
    def getWidget(self,options,action=None,name=None):
        widget = QWidget()
        widget.setAccessibleName(name)
        
        #Get options
        layout=self.getLayout(options)
        widget.setLayout(layout)
        
        #Setup buttons
        startBtn=QPushButton('Start')
        if action != None: startBtn.clicked.connect(action)
        layout.addRow(startBtn)
        
        return widget

    def addStateButton(self, boundState, text, action):
        layout=self.centralWidget().layout()
        self.onStateChange.connect(lambda state: self.stateWidgetHandle(state,boundState,text,action))

    #In this function I try to delete some buttons, but it is no elegant.
    def stateWidgetHandle(self, state, boundState, text, action):
        layout=self.centralWidget().layout()
        if boundState == state:
            if text not in [child.text() for child in self.centralWidget().children() if type(child) == QPushButton]:
                btn=QPushButton()
                btn.setText(text)
                btn.clicked.connect(action)
                layout.addRow(btn)
        else:
            for child in self.centralWidget().children():
                if(type(child) == QPushButton and child.text() ==  text):
                    layout.removeRow(child)

    def removeWidget(self,parent, objectType, text):
        for child in parent.children():
            if(type(child) == QLineEdit):
                print(vars(QLineEdit))
            if(type(child) == objectType and child.text() == text):
                parent.layout().removeRow(child)
                
                
