from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
import scipy.signal as signal
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from analysis import smooth
from widgets import h5Item
from ..acq4 import filterfuncs as acq4filter
####################################

class AnalysisModule(QtWidgets.QWidget):    

    def __init__(self, browser):    
        QtWidgets.QWidget.__init__(self)
            
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Event Detection'  
        ############################################
        
        # Get main browser and widgets
        self.browser = browser          
        self.plotWidget = browser.ui.dataPlotsWidget
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
        # Connect signals and slots
        self.plotWidget.eventSelected.connect(self.event_highlight)
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.eventDirection = QtWidgets.QComboBox()
        self.eventDirection.addItem('negative')
        self.eventDirection.addItem('positive')
        self.toolOptions.append([self.eventDirection])
        self.detectionTrace = QtWidgets.QComboBox()
        self.detectionTrace.addItem('trace')
        self.detectionTrace.addItem('derivative')
        self.toolOptions.append([self.detectionTrace])        
        self.derivativeDisplay = QtWidgets.QPushButton('Show derivative')
        self.toolOptions.append([self.derivativeDisplay])    
        self.eventThreshold = QtWidgets.QPushButton('Set Threshold')
        self.eventThreshold.setCheckable(True)
        self.eventThresholdDisplay = QtWidgets.QLabel('None')
        self.toolOptions.append([self.eventThreshold, self.eventThresholdDisplay])               
        self.eventNoiseSafety = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Noise Safety'), self.eventNoiseSafety])
        self.eventSmooth = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Smooth'), self.eventSmooth])
        self.eventMinDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Min Duration'), self.eventMinDuration])        
        self.eventMinInterval = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Min Interval'), self.eventMinInterval])             
        self.eventCheck = QtWidgets.QPushButton('Event Check')
        self.eventCheck.setCheckable(True)
        self.toolOptions.append([self.eventCheck])
        self.eventCutOut = QtWidgets.QPushButton('Cut events')
        self.toolOptions.append([self.eventCutOut])
        self.eventBaseline = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Duration'), self.eventDuration])           
        self.eventReplot = QtWidgets.QPushButton('Replot events')
        self.toolOptions.append([self.eventReplot])
        
        # Connect buttons to functions
        self.eventCutOut.clicked.connect(self.event_cut)
        self.eventThreshold.toggled.connect(self.show_thresholdCursor)   
        self.derivativeDisplay.clicked.connect(self.show_derivative)
        self.eventCheck.toggled.connect(self.event_check)
        self.eventReplot.clicked.connect(self.event_replot)              

        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)


    def func(self, browser):
        """ Temporary event detection function using amplitude
        threshold only. Noise safety is for when coming down from
        peak, go down an extra amount from threshold before starting
        to search for the next event.
        """
        ############################################
        # ANALYSIS FUNCTION
 
        # Read detection options 
        try:
            threshold = float(self.browser.ui.dataPlotsWidget.cursorThsPos)
        except NameError:
            aux.error_box('No threshold selected')
            return              

        try:
            noiseSafety = float(self.eventNoiseSafety.text())
            smoothFactor = float(self.eventSmooth.text())
            direction = str(self.eventDirection.currentText())
            minDuration = float(self.eventMinDuration.text())
            detectionTrace = str(self.detectionTrace.currentText())
            minInterval = float(self.eventMinInterval.text())
        except NameError:
            aux.error_box('Invalid detection value')
        bslWindow = 1.0
        slowestRise = 0.5
        #minEventInterval = 5000.0

        # Ensure that noise safety has the same sign as the threshold
        noiseSafety = np.sign(threshold) * abs(noiseSafety)

        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget

        # Get dt list and attrs for use in concatenated data
        dtList = aux.get_attr(self.browser.ui.dataPlotsWidget.plotDataItems, 'dt')
        dt = dtList[0]
        self.dt = dt
        item = self.browser.ui.dataPlotsWidget.plotDataItems[0]
        attrs = item.attrs

        # Get data currently plotted and concatenate in a single sweep
        data = []
        for item in plotWidget.plotDataItems:
            trace, c1 = aux.get_dataRange(plotWidget, item)
            data.append(trace)
        data = np.array(data).ravel()

        # Get derivative trace and filter
        dtrace = None
        if detectionTrace=='derivative':
            print(threshold)
            dtrace = np.diff(data)
            dtrace = acq4filter.besselFilter(dtrace, 2000, 1, dt/1000, 'low', True)

        # Smooth
        self.trace = data
        if smoothFactor > 1:
            data = smooth.smooth(data, window_len=smoothFactor, window='hanning')

        # Comparison functions  
        if direction=='negative':
            comp = lambda a, b: a < b
        elif direction=='positive':
            comp = lambda a, b: a > b
            
        # Correct times for dt    
        minEventInterval = minInterval/dt
        minDuration = minDuration/dt
        bslWindow = bslWindow/dt
        slowestRise = slowestRise/dt
            
        # Run detection
        eventCounter,i = 0,0 #+bslWindow/dt+slowestRise/dt
        iLastDetection = 0
        self.xOnsets, self.yOnsets = [], []
        bsl = 0
        if dtrace is not  None:
            detectionData = dtrace
        else:
            detectionData = data
        while i<len(detectionData):
            # Sliding baseline
            #bsl = np.mean(data[i-bslWindow-slowestRise:i])   
            if comp(detectionData[i]-bsl,threshold):
              print(i, i-iLastDetection)
              if i-iLastDetection>minEventInterval:  # Min inter-event interval
                self.xOnsets.append(i)
                self.yOnsets.append(data[i])
                eventCounter+=1
                iLastDetection = i
                while i<len(detectionData) and comp(detectionData[i]-bsl,(threshold-noiseSafety)):
                    i+=1 # skip values if index in bounds AND until the value is below/above threshold again
                if i-iLastDetection < minDuration: # Event is too brief
                    self.xOnsets.pop()
                    self.yOnsets.pop()
                    eventCounter-=1
              else:
                i+=1   # for min event interval   
            else:
                i+=1

        frequency = eventCounter/(len(data)*dt)*1000   # in Hz
        print(eventCounter, 'events detected at', frequency, 'Hz')

        # Store event onsets and peaks in h5 data tree
        results = []
        results.append(['trace', np.array(self.trace), attrs])
        results.append(['xOnsets', np.array(self.xOnsets)])
        results.append(['yOnsets', np.array(self.yOnsets)])
        results.append(['number', np.array([eventCounter])])
        results.append(['frequency', np.array([frequency])])
        aux.save_results(browser, 'Event_Detection', results)    

        # Plot results
        self.show_events(data, np.array(self.xOnsets), np.array(self.yOnsets), dt)

        # Turn cursors off (the plot has been cleared so there are no cursors displayed)    
        self.browser.ui.actionShowCursors.setChecked(False)
        plotWidget.cursor = False          
        ############################################            
        
        
    def event_cut(self):       
        # Get cutting parameters
        try:        
            baseline = float(self.eventBaseline.text())/self.dt
            duration = float(self.eventDuration.text())/self.dt 
        except NameError:
            aux.error_box('Invalid cutting value')

        # Cut out
        events, allAttrs = [], []
        for onset in self.xOnsets:
            eStart = onset-baseline
            eEnd = onset+duration
            eData = self.trace[eStart:eEnd]
            events.append(eData)
            attrs = {}
            attrs['dt'] = self.dt
            attrs['onset'] = onset
            allAttrs.append(attrs)

        # Store event waveforms in h5 data tree
        results = []
        #attrs = {}
        #attrs['dt'] = self.dt 
        for e in np.arange(0, len(events)):
            #attrs['onset'] = self.xOnsets[e]
            results.append(['event'+str(e), events[e], allAttrs[e]])  
        aux.save_results(self.browser, 'Events', results)
        

    def show_thresholdCursor(self):
        """ Show horizontal cursor to set threshold 
        """
        plotWidget = self.browser.ui.dataPlotsWidget
        if self.eventThreshold.isChecked():   
            plotWidget.cursorThsPos = 0
            plotWidget.cursorThs = pg.InfiniteLine(pos=plotWidget.cursorThsPos, angle=0, movable=True,
                                               pen=pg.mkPen('#FFD000', width=2))
            plotWidget.addItem(plotWidget.cursorThs)
            plotWidget.cursorThs.sigPositionChanged.connect(self.update_threshold)
        else:
            plotWidget.cursorThsPos = []
            plotWidget.removeItem(plotWidget.cursorThs)                    

        
    def update_threshold(self):
        plotWidget = self.browser.ui.dataPlotsWidget
        plotWidget.cursorThsPos = round(plotWidget.cursorThs.value(),4)
        self.eventThresholdDisplay.setText(str(plotWidget.cursorThsPos))

    def show_events(self, data, xOnsets, yOnsets, dt):
        self.plotWidget.clear()
        x = pgplot.make_xvector(data, dt)
        self.plotWidget.plot(x, data)
        self.plotWidget.plot(xOnsets*dt, yOnsets, pen=None, symbol='o', symbolPen='r', symbolBrush=None, symbolSize=7)

    def set_defaultValues(self):
        self.eventNoiseSafety.setText('5')
        self.eventSmooth.setText('1')
        self.eventMinDuration.setText('2')
        self.eventBaseline.setText('2')
        self.eventDuration.setText('20')
        self.eventMinInterval.setText('10')

    def show_derivative(self):
       """ Show derivative of plotted traces
       """
       for trace in self.plotWidget.plotDataItems:
           dt = float(trace.attrs['dt'])
           dtrace = np.diff(trace.data)
           dtrace = acq4filter.besselFilter(dtrace, 2000, 1, dt/1000, 'low', True)
           #dtrace = smooth.smooth(dtrace, window_len=5, window='hanning')
           x = pgplot.make_xvector(dtrace, dt)
           self.plotWidget.plot(x, dtrace,  pen=pg.mkPen('r'))

    def event_check(self):
        if self.eventCheck.isChecked():
            self.plotWidget.events = True
            self.plotWidget.eventOnsets = self.xOnsets*self.dt
        else:
            self.plotWidget.events = False
                        
    def event_replot(self):
        """ Replot event onsets over original trace       
        """
        self.trace, self.xOnsets, self.yOnsets = None, None, None
        item = self.browser.ui.workingDataTree.currentItem()
        for c in range(item.childCount()):
            if 'trace' in item.child(c).text(0): 
                self.trace = item.child(c).data
                self.dt = item.child(c).attrs['dt']
            if 'xOnsets' in item.child(c).text(0): self.xOnsets = item.child(c).data
            if 'yOnsets' in item.child(c).text(0): self.yOnsets = item.child(c).data
        if (self.trace is None) or (self.xOnsets is None) or (self.yOnsets is None): 
            aux.error_box('No event data found', infoText='Please select an item with trace and event onset data') 
            return
        else:
            self.show_events(self.trace, self.xOnsets, self.yOnsets, self.dt)
            
    def event_highlight(self):
        e = self.plotWidget.currentEvent
        #if eventPlotItem:
        #    self.plotWidget.removeItem(eventPlotItem)
        #else:
        #    eventPlotItem = pg.PlotDataItem([self.xOnsets[e]*self.dt], [self.yOnsets[e]], pen=None, symbol='o',
        #                                    symbolPen='c', symbolBrush='c', symbolSize=7)  
        #    self.plotWidget.addItem(eventPlotItem) 

        #self.plotWidget.plot([self.xOnsets[e]*self.dt], [self.yOnsets[e]], pen=None, symbol='o',
        #                symbolPen='c', symbolBrush='c', symbolSize=7)            
                  
            
''' create the eventPlotItem before, and turn it on and off with the event_check button/fun
    better to also select the starting event, otherwise it always starts from 0
'''
            
            
            
            
            
            
            

   


