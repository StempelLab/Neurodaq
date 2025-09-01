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
        self.entryName = 'Remove tracking spikes'  
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
        self.set_defaultValues()
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.nPoints = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Points'), self.nPoints])
        self.derivativeDisplay = QtWidgets.QPushButton('Show derivative')
        self.derivativeDisplay.setCheckable(True)
        self.toolOptions.append([self.derivativeDisplay])          
        self.derivativeThreshold = QtWidgets.QPushButton('Set derivative threshold')
        self.derivativeThreshold.setCheckable(True)
        self.derivativeThresholdDisplay = QtWidgets.QLabel('None')
        self.toolOptions.append([self.derivativeThreshold, self.derivativeThresholdDisplay])

        # Connect buttons to functions
        self.derivativeDisplay.toggled.connect(self.show_derivative)
        self.derivativeThreshold.toggled.connect(self.show_derivativeCursor)
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Get rid of spikes in the tracking traces, using the derivative
        to identify them. Substitute the corresponding point in the trace
        with the mean of the previous and following point.        

        Options:
        1) Threshold for the position derivative
        """

        ############################################
        # ANALYSIS FUNCTION      
    
        # Read options
        derivativeThs = float(self.plotWidget.derivativeCursorThsPos)
        nPoints = int(self.nPoints.text())

        # Get plotted data
        items = self.plotWidget.plotDataItems
        
        # Set up detection function
        if derivativeThs<0:         
            comp = lambda a, b: a < b
        else: 
            comp = lambda a, b: a > b
            
        # Go through traces    
        for item in items:
            # Detect spikes
            dtrace = np.diff(item.data)
            i = 0
            while i<len(dtrace):
                if comp(dtrace[i], derivativeThs):
                    item.data[i-nPoints:i+nPoints] = (item.data[i-nPoints]+item.data[i+nPoints])/2.           
                i+=1     

        # Replot data
        pgplot.replot(self.browser, self.plotWidget)
        ############################################  


    def show_derivative(self):
       """ Show derivative of plotted traces
       """
       for trace in self.plotWidget.plotDataItems:
           dt = float(trace.attrs['dt'])
           dtrace = np.diff(trace.data)
           x = pgplot.make_xvector(dtrace, dt)
           self.plotWidget.plot(x, dtrace,  pen=pg.mkPen('r'))
       
    def show_derivativeCursor(self, var):
        """ Show horizontal cursor to set Derivative threshold 
        """
        if self.derivativeThreshold.isChecked():   
            self.plotWidget.derivativeCursorThsPos = 0
            self.plotWidget.derivativeCursorThs = pg.InfiniteLine(pos=self.plotWidget.derivativeCursorThsPos,
                                                  angle=0, movable=True, pen=pg.mkPen('#FFD000', width=2))
            self.plotWidget.addItem(self.plotWidget.derivativeCursorThs)
            self.plotWidget.derivativeCursorThs.sigPositionChanged.connect(self.update_derivativeThreshold)
        else:
            self.plotWidget.derivativeCursorThsPos = []
            self.plotWidget.removeItem(self.plotWidget.derivativeCursorThs)                    
        
    def update_derivativeThreshold(self):
        self.plotWidget.derivativeCursorThsPos = round(self.plotWidget.derivativeCursorThs.value(),2)
        self.derivativeThresholdDisplay.setText(str(self.plotWidget.derivativeCursorThsPos))

    def set_defaultValues(self):
        self.nPoints.setText('2')



