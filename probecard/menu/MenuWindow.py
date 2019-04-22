from .Stateful import Stateful
from PyQt5.QtWidgets import *
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
                
                
