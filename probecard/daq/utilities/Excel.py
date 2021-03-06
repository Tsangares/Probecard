import xlsxwriter
import matplotlib
import time
import platform
if 'darwin' in platform.system().lower():
    import matplotlib
    matplotlib.use('TkAgg') #Mac support
matplotlib.use('TkAgg') #Mac support
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
from datetime import datetime
import os

OUTPUT_FOLDER="../output/excel/"
#Simply takes the data & writes it to an excel file.
def writeExcel(data,filename,time=True,excel_folder=None):
    if excel_folder is None: excel_folder=OUTPUT_FOLDER
#    if "Windows" not in platform.platform():
#        filename = tkFileDialog.asksaveasfilename(initialdir="~", title="Save data", filetypes=(("Microsoft Excel file", "*.xlsx"), ("all files", "*.*")))
    if not os.path.exists(excel_folder):
        os.makedirs(excel_folder)
    timestamp=datetime.today().strftime("_%Y_%b%d_%I.%M%p")
    if time:
        filename = filename+timestamp
    postfix='.xlsx'
    if '.xlsx' in filename:
        postfix=''
    file_url="%s%s%s"%(excel_folder,filename,postfix)
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



