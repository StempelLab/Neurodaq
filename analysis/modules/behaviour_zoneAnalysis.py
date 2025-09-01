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
        self.entryName = 'Two zone analysis '  
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
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.zoneDivider = QtWidgets.QPushButton('Set zone divider')
        self.zoneDivider.setCheckable(True)
        self.zoneDividerDisplay = QtWidgets.QLabel('None')
        self.toolOptions.append([self.zoneDivider, self.zoneDividerDisplay]) 
       
        # Connect buttons to functions
        self.zoneDivider.toggled.connect(self.show_zoneCursor)         
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Analyse tracking data for user defined zones in
        the arena. Currently the two zones are defined by
        a divider on the X or Y coordinates.
        
        Properties measured:
        1 - time spent in each zone normalized to total time
        2 - number of zone transitions 

        Options:
        1) Position of the divider between the two zones
        """

        ############################################
        # ANALYSIS FUNCTION      

        # Read options
        zoneDivider = float(self.plotWidget.zoneDividerCursorPos)

        # Get data and check cursors
        traces = self.plotWidget.plotDataItems
        dt = traces[0].attrs['dt']
        data, c1 = aux.get_dataRange(self.plotWidget, traces[0])
        
        # Get time in each zone
        zoneTime = [] 
        totalTime = float(len(data))
        zone1 = np.sum(data<zoneDivider)
        zone2 = totalTime-zone1
        zoneTime.append(zone1/totalTime)
        zoneTime.append(zone2/totalTime)
        
        # Get number of zone transitions
        transitions = np.sum(np.diff(data<zoneDivider))      

        # Store data
        results = []
        results.append(['Time', zoneTime])   
        results.append(['Transitions', [transitions]])
        aux.save_results(self.browser, 'Zone_analysis', results) 
        ############################################  

    def show_zoneCursor(self, var):
        """ Show horizontal cursor to set zone divider 
        """
        if self.zoneDivider.isChecked():   
            self.plotWidget.zoneDividerCursorPos = 0
            self.plotWidget.zoneDividerCursor = pg.InfiniteLine(pos=self.plotWidget.zoneDividerCursorPos, angle=0,
                                                               movable=True, pen=pg.mkPen('#FA5858', width=2))
            self.plotWidget.addItem(self.plotWidget.zoneDividerCursor)
            self.plotWidget.zoneDividerCursor.sigPositionChanged.connect(self.update_zoneDivider)
        else:
            self.plotWidget.zoneDividerCursorPos = []
            self.plotWidget.removeItem(self.plotWidget.zoneDividerCursor)                    
        
    def update_zoneDivider(self):
        self.plotWidget.zoneDividerCursorPos = round(self.plotWidget.zoneDividerCursor.value(),2)
        self.zoneDividerDisplay.setText(str(self.plotWidget.zoneDividerCursorPos))








