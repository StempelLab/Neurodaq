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
        self.entryName = 'Get trigger Events'  
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
        # Set default values
        self.set_defaultValues()        
    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.behaviourToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.stimType = QtWidgets.QComboBox()
        self.stimType.addItem('Visual')
        self.stimType.addItem('Pulse')
        self.stimTypeLabel = QtWidgets.QLabel('Type')
        self.toolOptions.append([self.stimTypeLabel, self.stimType])        
        self.trigger = QtWidgets.QComboBox()
        self.trigger.addItem('1')
        self.trigger.addItem('2')
        self.trigger.addItem('3')
        self.triggerLabel = QtWidgets.QLabel('Trigger level')
        self.toolOptions.append([self.triggerLabel, self.trigger])
        self.eventBaseline = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Duration'), self.eventDuration]) 
        self.stimProfile = QtWidgets.QCheckBox('Get stim profile')
        self.toolOptions.append([self.stimProfile])
        #self.eventCutOut = QtWidgets.QPushButton('Cut events')
        #self.toolOptions.append([self.eventCutOut])          

        # Connect buttons to functions
        #self.eventCutOut.clicked.connect(self.event_cut) 
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Analyse tracking data using triggered events 
        (e.g.: visual or laser stimulation)
  
        Analyses the currently plotted tracking trace. Currently it looks for 
        Visual or Pulse items in root, this will need changing if there are
        ever more than one per experiment.

        Overlays triggered events on tracking trace and gets
        trigger times for event cut out.

        Event Cut: extract snippets of tracking trace triggered on events trace
        (e.g.: loom or laser stimulation)

        Options:
        1) Baseline and Duration for event cut out
        2) Trigger level
        3) Type of stimulation
        4) Extract trigger profile (e.g.: spot diameter)
        """

        ############################################
        # ANALYSIS FUNCTION      
    
        # Read options
        level = int(self.trigger.currentText())
        stimType = str(self.stimType.currentText())

        # Get widgets
        self.plotWidget = browser.ui.dataPlotsWidget
        self.toolsWidget = browser.ui.oneDimToolStackedWidget
    
        # Iterate through root and get chosen trigger data
        #root = browser.ui.workingDataTree.invisibleRootItem()
        #for c in range(root.childCount()):
        #    if stimType in root.child(c).text(0): item = root.child(c)

        # Temporary 
        #if stimType=='Visual':
        #    if item.childCount()==1:
        #        triggers = item.child(0).data
        #    else:
        #        triggers = item.child(1).data
        #else:
        #    triggers = item.child(0).data

        # Get item with trigger start times
        item =  browser.ui.workingDataTree.selectedItems()[0]
        triggers = item.data
        
        # Make sure dt is matched
        dt = self.plotWidget.plotDataItems[0].attrs['dt']
        item.attrs['dt'] = dt
        
        # Get trigger times (in data points)
        tarray = np.arange(0, len(triggers))
        self.tevents = tarray[triggers==level]

        #HACK FOR OLD MOVIES - INPUT TIMES MANUALLY
        #self.tevents = [3595,7470,9435,11810,16560,26920,44850,54540]
        #self.tevents = [1220,4240,6040,7800,8970,10740,14760,16810,18080,22460,27680,
        #                29460,32250,35680,37600,41150,42230,43300,44230,45770]
        #self.tevents = [4400,11220,14300,15780,19960,25330,31740,32900,37500,40130]
        #self.tevents = [10290,10860,11350,11690,12060,12580,12980,13380,13730,14460,
        #                15100,16030,17590,22100,24660]
        #self.tevents = [6470,13960,24650]

        # Make infinte vertical lines on trigger events        
        for t in self.tevents:
            line = pg.InfiniteLine(pos=t*dt, angle=90, movable=False, pen=pg.mkPen('k', width=2))        
            self.plotWidget.addItem(line)

        # Automatically cut events and stimulation profiles
        #if self.stimProfile.isChecked():
        #   if stimType=='Visual':
        #       self.triggerProfileData = item.child(0).data          
        #       self.event_cut(profile=True)
        #else:
        #    self.event_cut()
        self.event_cut() 
        
        ############################################  

    def event_cut(self, profile=False):

        # Read options 
        baseline = float(self.eventBaseline.text())
        duration = float(self.eventDuration.text())
    
        # Get plotted tracking data
        trackData = self.plotWidget.plotDataItems[0].data

        # Get selected trigger data
        item = self.browser.ui.workingDataTree.currentItem()
        triggers = item.data
        
        # Deal with dt
        dt = self.plotWidget.plotDataItems[0].attrs['dt']
        item.attrs['dt'] = dt

        # Extract events        
        events, stimProfiles = [], []
        for t in self.tevents:
            event = trackData[t-int(baseline/dt):t+int(duration/dt)]
            events.append(event)
            if profile:
                eventProfile = self.triggerProfileData[t-int(baseline/dt):t+int(duration/dt)]
                stimProfiles.append(eventProfile)                

        # Store data
        results = []
        attrs = {}
        attrs['dt'] = dt 
        attrs['t0'] = baseline  # in sampling points
        for e in np.arange(0, len(events)):
            attrs['trigger_time'] = self.tevents[e]  # in sampling points 
            results.append(['event'+str(e), events[e], attrs])  
        aux.save_results(self.browser, 'Events', results)
                
        if profile:
            results = []
            for e in np.arange(0, len(stimProfiles)):
                attrs['trigger_time'] = self.tevents[e]  # in sampling points 
                results.append(['stim'+str(e), stimProfiles[e], attrs])  
            aux.save_results(self.browser, 'Stimulation Profiles', results)     
        

    def set_defaultValues(self):
        self.eventBaseline.setText('200')
        self.eventDuration.setText('200')





