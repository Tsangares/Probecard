import json
from .ValueHandler import ValueHandler
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow,QCheckBox
#Saveable UI, a way to handle the data in a UI
#Uses ValueHandler but does not inherit it.
class Saveable(QMainWindow,ValueHandler):
    onLoad = pyqtSignal(str)
    onSave = pyqtSignal(str)

    def saveSettings(self, filename="settings.json"):
        saveData=json.dumps(self.getData())
        with open(filename, "w") as f:
            f.write(saveData)
        self.onSave.emit('saved')

    #Get state from recently loaded save and deal with it.
    def setState():
        pass

    def exit(self):
        self.saveSettings(filename="settings.json")
    
    def loadSettings(self,filename="settings.json"):
        data=None
        try:
            with open(filename) as f:
                data=json.loads(f.read())
                f.close()
            if data != None:
                for key,field in data.items():
                    try:
                        obj=self.getValue(key)
                        if type(obj) == QCheckBox:
                            obj.setCheckState(data[key])
                        else:
                            obj.setText(data[key])
                    except KeyError:
                        print("Nothing saved for %s"%key)
                self.onLoad.emit("loaded")
        except json.decoder.JSONDecodeError:
            print("Save file is corrupted, please delete %s"%filename)            
        except FileNotFoundError:
            print("No settings file.")

    def getSettings(self,filename="settings.json"):
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
        self.loadSettings(filename="settings.json")
