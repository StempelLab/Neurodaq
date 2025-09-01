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
        self.entryName = 'Get distance travelled'  
        ############################################
        
        # Get main browser and widgets
        self.browser = browser       
        self.plotWidget = browser.ui.dataPlotsWidget
        self.toolsWidget = browser.ui.oneDimToolStackedWidget   
        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.behaviourToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()
        # Set default values
        #self.set_defaultValues()
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.pixelConversion = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('cm/pixel'), self.pixelConversion])

        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Calculate distance travelled from the X and Y tracking coordinates,
        currently plotted.        

        Options:
        1) pixel to cm conversion factor
        """

        ############################################
        # ANALYSIS FUNCTION      
    
        # Read options
        try:
            conversionFactor = int(self.pixelConversion.text())
        except ValueError:
            aux.error_box('Invalid pixel conversion factor')

        # Get plotted data
        #items = self.plotWidget.plotDataItems
        
           
        # Replot data
        #pgplot.replot(self.browser, self.plotWidget)
        ############################################  


    #def set_defaultValues(self):
    #    self.nPoints.setText('2')



