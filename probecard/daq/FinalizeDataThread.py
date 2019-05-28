from PyQt5.QtCore import QThread, pyqtSignal
from io import BytesIO
from time import sleep
from random import random
from .utilities import writeExcel,attachFile,send_mail
import os

'''
Input an email address and a dictionary.
Send an email with the dictionary in an excel format.
'''
excel_folder = os.path.expanduser("~/Desktop/probecard_output/excel/")
if not os.path.exists(excel_folder):
    os.makedirs(excel_folder)
class FinalizeDataThread(QThread):
    done=pyqtSignal(str)
    log=pyqtSignal(str)
    #Do not put a file-extension in filename; paths are ok.
    def __init__(self,filename,email,data,figure=None):
        super(FinalizeDataThread,self).__init__()
        self.filename=filename
        self.email=email
        self.data=data
        self.figure=figure
        
    def run(self):
        self.log.emit("Writing excel.")
        filename=writeExcel(self.data,self.filename,excel_folder=excel_folder)
        files=[]
        if self.figure is not None:
            files.append((self.figure, "log"))
        self.log.emit("Sending email.")
        send_mail(filename,self.email,files=files)
        print("Data saved and email sent.")
        sleep(.5)
        self.done.emit('done')
