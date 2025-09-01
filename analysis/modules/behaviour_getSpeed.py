from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
from widgets import h5Item
import pyqtgraph as pg
from ..acq4 import filterfuncs as acq4filter
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Get speed'  
        ############################################
        
        # Get main browser
        self.browser = browser          
        # Add entry to AnalysisSelectWidget         
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.behaviourToolSelect
        selectWidget.model.appendRow(selectItem)        
        # Add entry to tool selector        
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()
       
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.longAxisBox = QtWidgets.QCheckBox('Long axis only')
        self.toolOptions.append([self.longAxisBox]) 
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Convert X-Y coordinates into speed
        
        User selects Real-Time Coordinates item and speed is
        added as a child
        
        Options:
        1) use only the long axis (ignore short axis entirely)
        """

        ############################################
        # ANALYSIS FUNCTION      
    
        # Get widgets
        self.plotWidget = browser.ui.dataPlotsWidget
        self.toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Get X and Y data from selected coordinates
        x, y = [], []
        parentItem = browser.ui.workingDataTree.selectedItems()[0]
        for i in range(parentItem.childCount()):
            item = parentItem.child(i)
            if 'X' in item.text(0):
                x = item.data
            elif 'Y' in item.text(0):
                y = item.data
        if len(x)==0 or len(y)==0:   
            aux.error_box('XY coordinates not found')
            return

        # Calculate speed
        d = []
        dt = item.attrs['dt']
        for i in range(1, len(x)):
            xmov = x[i] - x[i-1]
            ymov = y[i] - y[i-1]
            if self.longAxisBox.isChecked():
                d.append(xmov)
            else:
                d.append(np.sqrt((xmov**2) + (ymov**2)))
        d.append(d[-1]) # so that it has the same number of points as original
        speed = d # px/frame  > px/s = speed/(1./dt) with dt in seconds

        # Store data
        if self.longAxisBox.isChecked():
            speedItem = h5Item(['longAxis_speed'])
        else:
            speedItem = h5Item(['speed'])
        speedItem.data = np.array(speed)
        parentItem.addChild(speedItem)
        
        ############################################  



