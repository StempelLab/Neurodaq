from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Baseline'  
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
        self.keepData = QtWidgets.QCheckBox('Keep original data')
        self.toolOptions.append(self.keepData)
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Subtract a baseline from the currently plotted traces.
        Baseline is the average of all datapoints between the 
        current position of the data cursors. 
    
        Options:
        1) keep original traces intact and create processed copies
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget   

        # Copy data if required
        if self.keepData.isChecked():
            aux.make_data_copy(browser, plotWidget)
    
        # Get dt
        dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]

        # Make average between cursors and subract for each trace 
        for item in plotWidget.plotDataItems:                        
            bslData, c1 = aux.get_dataRange(plotWidget, item)             
            bsl = np.mean(bslData)
            item.data = item.data - bsl
            item.analysis['baselineStart'] = c1 
            item.analysis['baselineEnd'] = c1+len(bslData)
            
        # Re-plot data
        pgplot.replot(browser, plotWidget)     
         
        ############################################            
        

