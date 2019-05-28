if __package__ in [None,""]:
    from BaseProbecardThread import *
    from BasicDaqWindow import *
else:
    from .BaseProbecardThread import *
    from .BasicDaqWindow import *

if __name__=='__main__':
    #Make a test
    
    #Create basic GUI
    gui=QApplication(['test'])
    daq=BasicDaqWindow()
    gui.window=daq

    #Create a plotting thread
    options={
        'debug': True
    }
    thread=BaseProbecardThread(options)
    thread.newData.connect(daq.addPoint)
    thread.start()
    
    gui.exec_()
