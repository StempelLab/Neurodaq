from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from ..acq4 import filterfuncs as acq4filter
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Filter'  
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
        # Set default values
        self.set_defaultValues()
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItem('Bessel')
        #self.comboBox.addItem('Butterworth')
        self.toolOptions.append([self.comboBox])        
        self.comboPass = QtWidgets.QComboBox()
        self.comboPass.addItem('Low pass')
        self.comboPass.addItem('High pass')                
        self.toolOptions.append([self.comboPass])
        self.filterCutoff = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Cut off'), self.filterCutoff])  
        self.filterOrder = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Order'), self.filterOrder]) 
        self.filterDirection = QtWidgets.QCheckBox('Bidirectional')
        self.toolOptions.append([self.filterDirection])               
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Filter traces
    
        Options:
        1) Filter type (currently Bessel only)
        2) Filter parameters
        
        Note: filter frequencies are in Hz, make sure dt is in seconds
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        # Get options
        btype = str(self.comboPass.currentText())
        if 'Low' in btype:
            btype = 'low'
        elif 'High' in btype:
            btype = 'high'
        try:    
            cutoff = float(self.filterCutoff.text())
            order = float(self.filterOrder.text())
        except ValueError:
            aux.error_box('Invalid Cut off or Order value')
            return
        bidir = self.filterDirection.isChecked()
    
        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Get parent text of plotted items
        try:
            parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
        except AttributeError:   # Parent = None
            parentText = 'Data'
    
        # Filter data
        results, itemsToPlot = [], [] 
        for item in plotWidget.plotDataItems:  
            # Copy attributes and add some new ones
            attrs = item.attrs
            attrs['filter_type'] = btype
            attrs['filter_cutoff'] = cutoff
            attrs['filter_order'] = order
        
            # Filter
            traceFilter = acq4filter.besselFilter(item.data, cutoff, order, float(item.attrs['dt'])/1000, btype, bidir)
            results.append([item.text(0), traceFilter, attrs])
        
            # Store filtered traces            
            filterItem = aux.make_h5item('filter', traceFilter, item.attrs)
            itemsToPlot.append(filterItem)

        # Plot results
        pgplot.plot_multipleData(browser, plotWidget, itemsToPlot, clear=False, color='#F2EF44')

        # Store results
        aux.save_results(browser, parentText+'_filter', results)     
         
        ############################################  

    def set_defaultValues(self):
        self.filterCutoff.setText('2000')
        self.filterOrder.setText('1')
        self.filterDirection.setCheckState(True)
        self.filterDirection.setTristate(False)



