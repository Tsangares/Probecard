import xlsxwriter
import matplotlib
import time
import platform
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from datetime import datetime
import os
matplotlib.use("TkAgg")

OUTPUT_FOLDER="./excel/"
#Simply takes the data & writes it to an excel file.
def writeExcel(data,filename,time=True):
#    if "Windows" not in platform.platform():
#        filename = tkFileDialog.asksaveasfilename(initialdir="~", title="Save data", filetypes=(("Microsoft Excel file", "*.xlsx"), ("all files", "*.*")))
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    timestamp=datetime.today().strftime("_%Y_%b%d_%I.%M%p")
    if time:
        filename = filename+timestamp
    file_url="%s%s.xlsx"%(OUTPUT_FOLDER,filename)
    workbook=xlsxwriter.Workbook(file_url)
    worksheet=workbook.add_worksheet()
    #Get parameters
    #assuming data is map key of variables, place them all into a grid.
    column=0
    for key,values in sorted(list(data.items()), key=lambda item: item[0]!='Voltage'):
        worksheet.write(0,column,key)
        for i,value in enumerate(values):
            worksheet.write(i+1,column,float(value)) #i+1 because the title is above
        column+=1
    #chart?
    workbook.close()
    return file_url



