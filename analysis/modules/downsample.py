from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from analysis import smooth
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Downsample'  
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
        self.points = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Points'), self.points])        
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Downsample data by taking one point every N points
    
        Options:
        1) Number of points
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        # Get options
        try:
            nPoints = int(self.points.text())
        except ValueError:
            aux.error_box('Invalid number of points')
            return
    
        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Get parent text of plotted items
        try:
            parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
        except AttributeError:   # Parent = None
            parentText = 'Data'
    
        # Smooth data
        results, itemsToPlot = [], [] 
        for item in plotWidget.plotDataItems:  
            # Copy attributes and add some new ones
            attrs = dict(item.attrs)
            attrs['dt'] = attrs['dt']*nPoints
        
            # Downsample
            traceDsampled = item.data[0::nPoints]
            results.append([item.text(0), traceDsampled, attrs])
        
            # Store smoothed item
            dSampledItem = aux.make_h5item('smooth', traceDsampled, attrs)
            itemsToPlot.append(dSampledItem)

        # Plot results
        pgplot.plot_multipleData(browser, plotWidget, itemsToPlot, clear=False, color='#F2EF44')

        # Store results
        aux.save_results(browser, parentText+'_dSample', results)     
         
        ############################################  
      
      
