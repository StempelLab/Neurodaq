from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Make image series'  
        ############################################
        
        # Get main browser and widgets
        self.browser = browser       
        self.plotWidget = browser.ui.dataPlotsWidget
        self.toolsWidget = browser.ui.oneDimToolStackedWidget   
        self.canvas =  browser.ui.mplWidget.canvas
        self.ax = browser.ui.mplWidget.canvas.ax

        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.imageToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.imageToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        #self.plotAxisOption = QtWidgets.QCheckBox('Long axis over time')
        #self.toolOptions.append([self.plotAxisOption])      
        ############################################        

        #stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Convert selected images to a image series

        Options:
        """

        ############################################
        # ANALYSIS FUNCTION      

        # Get selected images
        items = browser.ui.workingDataTree.selectedItems()
        
        # Make 3D array
        image = [i.data for i in items]
        image = np.array(image)
        
        # Store
        item = make_h5item('image_series', image, None)
        browser.ui.workingDataTree.addTopLevelItem(item)

        ############################################  




