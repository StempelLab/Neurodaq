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
        self.entryName = 'Trigger Event Properties'  
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
        self.nestThreshold = QtWidgets.QPushButton('Set nest threshold')
        self.nestThreshold.setCheckable(True)
        self.nestThresholdDisplay = QtWidgets.QLabel('None')
        self.toolOptions.append([self.nestThreshold, self.nestThresholdDisplay])  
        self.derivativeDisplay = QtWidgets.QPushButton('Show derivative')
        self.derivativeDisplay.setCheckable(True)
        self.toolOptions.append([self.derivativeDisplay])          
        self.derivativeThreshold = QtWidgets.QPushButton('Set derivative threshold')
        self.derivativeThreshold.setCheckable(True)
        self.derivativeThresholdDisplay = QtWidgets.QLabel('None')
        self.toolOptions.append([self.derivativeThreshold, self.derivativeThresholdDisplay])

        # Connect buttons to functions
        self.nestThreshold.toggled.connect(self.show_nestCursor)  
        self.derivativeDisplay.toggled.connect(self.show_derivative)
        self.derivativeThreshold.toggled.connect(self.show_derivativeCursor)
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Get some properties of currently plotted tracking trigger events
        extracted with behaviour_triggerEvents.py module

        Properties measured:
        1 - failures to escape
        2 - latency to escape
        3 - time to reach the nest
        4 - average speed of escape
        5 - peak speed during escape

        Extracted events have useful attributes:
        t0 : data point of the trigger from the start of the event
        trigger_time : data point of the trigger from the start of the original
                       tracking trace

        Options:
        1) Threshold for the nest long-axis coordinate
        2) Threshold for the position derivative (to measure response latency)
        """

        ############################################
        # ANALYSIS FUNCTION      
    
        # Read options
        nestPos = float(self.plotWidget.nestCursorThsPos)
        derivativeThs = float(self.plotWidget.derivativeCursorThsPos)

        # Get plotted events
        events = self.plotWidget.plotDataItems
        
        # Go through events
        failures = []
        latencies, timeToNest, avgSpeed, maxSpeed = [], [], [], []
        comp = lambda a, b: a < b
        for event in events:
        
            # Get data range          
            #data, c1 = aux.get_dataRange(plotWidget, event)

            # Mark failures depending on position reached nest
            if np.sum(event.data<nestPos)==0:
                failures.append(1)
            else:
                failures.append(0)

                # Get latency to reaction
                t0 = event.attrs['t0']
                i = t0  # start from stimulus trigger
                dtrace = np.diff(event.data)
                while i<len(dtrace):
                    if comp(dtrace[i], derivativeThs):
                        latencies.append(i-t0)
                        break
                    i+=1     

                # Get latency to nest
                i = t0
                while i<len(event.data):
                    if comp(event.data[i], nestPos):
                        timeToNest.append(i-t0)
                        break
                    i+=1

                # Get other measures         
                avgSpeed.append(np.mean(dtrace[t0:i]))
                maxSpeed.append(dtrace[t0:i].min())

        # Store data
        results = []
        results.append(['Failures', failures])
        results.append(['Latencies', latencies])  
        results.append(['Time_to_nest', timeToNest])
        results.append(['Average_speed', avgSpeed])
        results.append(['Max_speed', maxSpeed])   
        aux.save_results(self.browser, 'Event_measurements', results)  
        ############################################  


    def show_derivative(self):
       """ Show derivative of plotted traces
       """
       for trace in self.plotWidget.plotDataItems:
           dt = float(trace.attrs['dt'])
           dtrace = np.diff(trace.data)
           x = pgplot.make_xvector(dtrace, dt)
           self.plotWidget.plot(x, dtrace,  pen=pg.mkPen('r'))

    def show_nestCursor(self, var):
        """ Show horizontal cursor to set Nest threshold 
        """
        if self.nestThreshold.isChecked():   
            self.plotWidget.nestCursorThsPos = 0
            self.plotWidget.nestCursorThs = pg.InfiniteLine(pos=self.plotWidget.nestCursorThsPos, angle=0,
                                                           movable=True, pen=pg.mkPen('#FA5858', width=2))
            self.plotWidget.addItem(self.plotWidget.nestCursorThs)
            self.plotWidget.nestCursorThs.sigPositionChanged.connect(self.update_nestThreshold)
        else:
            self.plotWidget.nestCursorThsPos = []
            self.plotWidget.removeItem(self.plotWidget.nestCursorThs)                    
        
    def update_nestThreshold(self):
        self.plotWidget.nestCursorThsPos = round(self.plotWidget.nestCursorThs.value(),2)
        self.nestThresholdDisplay.setText(str(self.plotWidget.nestCursorThsPos))
       
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




