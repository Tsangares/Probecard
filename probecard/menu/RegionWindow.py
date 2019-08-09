from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .MenuWidget import MenuWidget
from .Saveable import Saveable
class RegionWindow(Saveable):
    def __init__(self):
        super(RegionWindow,self).__init__()
        self.regions=[]
        
    def buildRegionButtons(self,layout):
        if not issubclass(type(layout),QLayout): raise(Exception("%s must be %s"%(layout,QLayout)))
        self.regionsLayout=layout
        self.addRegionBtn=QPushButton('Add Region')
        self.delRegionBtn=QPushButton('Delete Region')
        layout.addRow(self.delRegionBtn,self.addRegionBtn)
        self.addRegionBtn.clicked.connect(self.addRegion)
        self.delRegionBtn.clicked.connect(self.delRegion)
        self.recoverRegions()
        
    def temp(self,*args):
        for a in args:
            print(a)
        
        
    def addRegion(self,msg=None):
        layout=self.regionsLayout
        key='region_%s'%len(self.regions)
        labels=self.getLabelFromKey(key)
        dbkeys=self.getDbKeyFromKey(key)
        startBtn=None
        if len(self.regions) >= 1:
            prevKey='region_%s'%(len(self.regions)-1)
            prevEndButton=self[self.getDbKeyFromKey(prevKey)['end']]
            self[dbkeys['start']]=prevEndButton
        else:
            startBtn=self.getLineEdit(dbkeys['start'])
            startBtn.setPlaceholderText("0")
        stepsBtn=self.getLineEdit(dbkeys['steps'])
        stepsBtn.setPlaceholderText("0")
        endBtn=self.getLineEdit(dbkeys['end'])
        endBtn.setPlaceholderText("0")
        self.regions.append(key)
        if startBtn is not None:
            layout.addRow(QLabel(labels['start']), startBtn)
        layout.addRow(QLabel(labels['steps']), stepsBtn)
        layout.addRow(QLabel(labels['end']), endBtn)
        
    def getLabelFromKey(self,key):
        return {
            'start': key+" Start (V)",
            'end': key+" End (V)",
            'steps': key+" Steps (#)",
        }
    def getDbKeyFromKey(self,key):
        return {
            'start': key+'_start',
            'end': key+'_end',
            'steps': key+'_steps',
        }

    #Remove labels from labels
    def delRegion(self,msg=None):
        if len(self.regions) == 1: return
        key=self.regions[-1]
        self.regions.remove(key)
        labels=self.getLabelFromKey(key)
        for k,label in labels.items():
            self.removeWidget(self.regionsLayout, QLabel, label)
        dbkeys=self.getDbKeyFromKey(key)
        for k,dbkey in dbkeys.items():
            self.delete(dbkey)

    #Build regions based on save file.
    def recoverRegions(self):
        settings=self.getSettings()
        if settings is None: return
        regions = [ key for key,value in settings.items() if 'region' in key  and 'start' in key ]
        for region in range(len(regions)):
            self.addRegion()
        

