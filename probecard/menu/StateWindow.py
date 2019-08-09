from .Saveable import Saveable
from .ValueHandler import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from abc import ABCMeta,abstractmethod
#Menu Window inherits Stateful <- Saveable <- QMainWindow & ValueHandler
# It is mainly suposed to be a QMainWindow object with functions
# that assist with creating a casual input fields and buttons.
# The stateful aspect is for coordinating similar but slightly different pages
# Saveable means it autosaves fields on exit.
# Valuehadler is essentially a database to make running the experiment easier.
# The tool bar is a set of radio buttons representing possible states.
class Stateful(Saveable):
    onStateChange = pyqtSignal(str)
    def __init__(self):
        super(Stateful,self).__init__()
        self.state=None
        
    def getState(self):
        return self.state

    def setState(self,state):
        self['state'].setValue(state)
        self.state=state
        self.onStateChange.emit(state)
        return state

class StateWindow(Stateful):
    def __init__(self):
        super(StateWindow,self).__init__()
        self.states=[]
        self.onLoad.connect(lambda: self.setState(self['state'].getValue()))
        self.onStateChange.connect(self.purgeState)
        self.toolbar = QToolBar()
        #self.addToolBar(self.toolbar)

        #Setup a toolbar
        toolbarContainer = QWidget()
        self.stateLayout=QHBoxLayout(toolbarContainer)
        self['state']=LineEdit()
        self.toolbar.addWidget(toolbarContainer)
        
        self.stateWidget=QFrame()
        QFormLayout(self.stateWidget)
        self.stateLabel=QLabel("Page Specfic Fields")
        self.stateLabel.setStyleSheet("color: #aaa;font-family: monospace;")
        self.stateWidget.layout().addRow(self.stateLabel)
        self.stateCache={}

    def addState(self,state):
        self.states.append(state)
        btn=QRadioButton(state)
        btn.clicked.connect(lambda a=True,b=btn: self.setState(b.text()))
        self.stateLayout.addWidget(btn)

        
    #Call refreshToolbar when the state changes.
    def setState(self,state):
        self.refreshToolbar(state)
        return super(StateWindow,self).setState(state)
    
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

    #Converts a dict of <name,key> objects to a form.
    #The `name` is a human readable descriptior,
    # and `key` pulls options from the gui to give to the experiment's code
    def getLayout(self,options):
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

    def checkState(self,state):
        if state not in [e[0] for e in self.stateCache.items()]:
            self.stateCache[state]=[]

    def addStateWidget(self,state,*args):
        self.checkState(state)
        for widget in args:
            self.stateCache[state].insert(0,widget)
        self.purgeState(self.getState())

    def addStateButton(self, boundState, text, action=None):
        btn=QPushButton(text)
        if action is not None: btn.clicked.connect(action)
        self.addStateWidget(boundState,btn)
        
    def purgeState(self,currentState):
        self.checkState(currentState)
        #Destruction
        for child in self.stateWidget.children():
            hide=self.stateCache[currentState]
            if len(self.stateCache[currentState])>0:
                hide+=[self.stateLabel]
            if issubclass(type(child),QWidget) and child not in hide:
                child.hide()
        #Creation
        for widget in self.stateCache[currentState]:
            if widget not in self.stateWidget.children():
                if issubclass(type(widget),tuple):
                    self.stateWidget.layout().addRow(widget[0],widget[1])
                else:
                    self.stateWidget.layout().addRow(widget)
            if issubclass(type(widget),tuple):
                widget[0].show()
                widget[1].show()
            else:
                widget.show()
                
                
