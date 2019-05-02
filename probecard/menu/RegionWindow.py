from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from .MenuWindow import MenuWindow
from .Saveable import Saveable
class RegionWindow(Saveable):

    def buildRegionButtons(self,layout):
        self.regionsLayout=layout
        self.addRegionBtn=QPushButton('Add Region')
        self.delRegionBtn=QPushButton('Delete Region')
        layout.addRow(self.delRegionBtn,self.addRegionBtn)
        self.addRegionBtn.clicked.connect(self.addRegion)
        self.delRegionBtn.clicked.connect(self.delRegion)
        self.regions=[]
        self.recoverRegions()
        
    def recoverRegions(self):
        settings=self.getSettings()
        if settings is None: return
        regions = [ key for key,value in settings.items() if 'region' in key  and 'start' in key ]
        for region in range(len(regions)):
            self.addRegion()
        
        
    def addRegion(self,msg=None):
        layout=self.regionsLayout
        key='region_%s'%len(self.regions)
        labels=self.getLabelFromKey(key)
        dbkeys=self.getDbKeyFromKey(key)
        startBtn=self.getLineEdit(dbkeys['start'])
        if len(self.regions) >= 1:
            prevKey='region_%s'%(len(self.regions)-1)
            prevEndButton=self[self.getDbKeyFromKey(prevKey)['end']]
            startBtn.setReadOnly(True)
            startBtn.setStyleSheet('background-color:#eee;color:gray')
            prevEndButton.editingFinished.connect(lambda: startBtn.setText(prevEndButton.text()))
            startBtn.setText(prevEndButton.text())
        self.regions.append(key)
        endBtn=self.getLineEdit(dbkeys['end'])
        stepsBtn=self.getLineEdit(dbkeys['steps'])
        endBtn.setText("0")
        stepsBtn.setText("0")
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
