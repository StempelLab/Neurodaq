from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
import sys
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Average'  
        ############################################
        
        # Get main browser
        self.browser = browser          
        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.oneDimToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()

    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.showTraces = QtWidgets.QCheckBox('Show traces')
        self.storeResult = QtWidgets.QCheckBox('Store result')
        self.sdBox = QtWidgets.QCheckBox('SD')
        self.semBox = QtWidgets.QCheckBox('SEM')       
        self.toolOptions.append(self.showTraces)
        self.toolOptions.append(self.sdBox)
        self.toolOptions.append(self.semBox)
        self.toolOptions.append(self.storeResult)      
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Calculate average trace from currently plotted traces. If cursors are
        selected the average is calculated for the range within the cursors.

        Options:
        1) create new entry in Working Data tree with the result
        2) plot average with orginal traces
        3) caclulate SD and SEM
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget   
        results = []

        # Get data and cursors
        data = []
        for item in plotWidget.plotDataItems:
            dt = item.attrs['dt']
            dataRange, c1 = aux.get_dataRange(plotWidget, item)    
            data.append(dataRange)   
        data = np.array(data)

        # Calculate average and make h5item for plotting
        try:
            #avgData = np.nanmean(data[:, c1:c2], 0)
            avgData = np.mean(data, 0)
            avgItem = aux.make_h5item('avg', avgData, plotWidget.plotDataItems[0].attrs)
            results.append(['avg_trace', avgData, item.attrs])  
        except ValueError:  
            aux.error_box('Cannot calculate average on data with different lengths', sys.exc_info(),
                          'Please ensure that all traces have the same length') 
            return

        # Calculate SD and SEM
        if self.sdBox.isChecked():
            #sdData = np.nanstd(data[:, c1:c2], 0)
            sdData = np.std(data, 0)            
            avgPlusSDItem = aux.make_h5item('avg+sd', avgData+sdData, plotWidget.plotDataItems[0].attrs)
            avgMinusSDItem = aux.make_h5item('avg-sd', avgData-sdData, plotWidget.plotDataItems[0].attrs)
            results.append(['avg+sd', avgData+sdData, item.attrs])  
            results.append(['avg-sd', avgData-sdData, item.attrs])  
 
        if self.semBox.isChecked():
            #semData = np.nanstd(data[:, c1:c2], 0)/np.sqrt(len(data))
            semData = np.std(data, 0)/np.sqrt(len(data))
            avgPlusSEMItem = aux.make_h5item('avg+sem', avgData+semData, plotWidget.plotDataItems[0].attrs)
            avgMinusSEMItem = aux.make_h5item('avg-sem', avgData-semData, plotWidget.plotDataItems[0].attrs)
            results.append(['avg+sem', avgData+semData, item.attrs])  
            results.append(['avg-sem', avgData-semData, item.attrs])  

        # Plot data
        if self.showTraces.isChecked(): 
            clear = False
        else:
            clear = True
        pgplot.browse_singleData(browser, plotWidget, avgItem, clear=clear, color='r')

        # Store data
        if self.storeResult.isChecked():     
            aux.save_results(browser, item.parent().text(0)+'_average', results) 
                 
        ############################################  
        
        
        
        
        
