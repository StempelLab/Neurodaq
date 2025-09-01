from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
import sys, traceback
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from ..acq4 import filterfuncs as acq4filter
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Average trials'  
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
        self.trialsNumber = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Number of trials'), self.trialsNumber])                
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Average trials for protocols with more than one sweep
        (e.g.: current or voltage steps)
    
        Options:
        1) Number of trials contained in the selected traces
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        # Get options
        try:
            numberOfTrials = int(self.trialsNumber.text())
        except ValueError:
            aux.error_box('Please input a valid number of trials')
            return
    
        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Get parent text of plotted items
        try:
            parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
        except AttributeError:   # Parent = None
            parentText = 'Data'
    
        # Get data and attributes
        data = aux.get_data(self.browser)
        item = plotWidget.plotDataItems[0]
        
        # Reshape data and average
        try:
            data.shape = (numberOfTrials, data.shape[0]/numberOfTrials, data.shape[1])
            avg = data.mean(axis=0)
        
            # Make h5 items
            results, itemsToPlot = [], []        
            for sweep in avg:  
                #sweepItem = aux.make_h5item('sweep', sweep, item.attrs)
                results.append(['sweep', sweep, item.attrs])
        
                # Store average sweep            
                sweepItem = aux.make_h5item('sweep', sweep, item.attrs)
                itemsToPlot.append(sweepItem)

            # Plot results
            pgplot.plot_multipleData(browser, plotWidget, itemsToPlot, clear=False, color='#F2EF44')

            # Store results        
            aux.save_results(browser, parentText+'_trialsAvg', results)     
        
        except ValueError: 
            aux.error_box('The number of sweeps and trials do not match', sys.exc_info())          
        ############################################  

