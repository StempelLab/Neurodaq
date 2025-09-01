from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import os
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
import re
from widgets import h5Item
from ..acq4 import filterfuncs as acq4filter
from moviepy.editor import *
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Tag analysis'  
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
        #self.eventsBox = QtWidgets.QCheckBox('Get events')
        #self.toolOptions.append([self.eventsBox])
        self.eventBaseline = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Duration'), self.eventDuration]) 
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Extract data from traces plotted in the video tab by searching
        for tags. Video stream item has to be selected, as this it what
        holds the tags. Tags are in ms from start of video stream.

        Options:
        1) Baseline and duration of tag events (in ms)
        """


        ############################################
        # ANALYSIS FUNCTION      

        # Read options 
        self.baseline = int(self.eventBaseline.text())
        self.duration = int(self.eventDuration.text())
    
        # Get video stream item
        item = browser.ui.workingDataTree.selectedItems()[0]
        if ('video' in item.attrs) and (item.attrs['video']=='True'):
            pass
        else:
            aux.error_box('Selected item is not a video stream')

        # Get tags (list with times in ms)
        tagStr = 'VideoTag_'+str(browser.ui.videoTagSelection.currentText())
        tags = item.attrs[tagStr]

        # Get plotted data to process
        self.dataItems = browser.ui.dataVideoWidget.plotsWidget.plotDataItems

        # Prepare items
        root = browser.ui.workingDataTree.invisibleRootItem()
        tagsParentItem = h5Item([str('Tag_events')])
        root.addChild(tagsParentItem)    

        # Extract events
        c = 0
        for tag in tags:
            tagItem =  h5Item([str('Tag_')+str(c)])         
            tagsParentItem.addChild(tagItem)
            self.getEvents(tag, tagItem)         
            c+=1   

        ############################################  
    def getEvents(self, tagTime, tagItem):
        startTime = tagTime-self.baseline
        endTime = tagTime+self.duration
        c = 0
        for i in self.dataItems:
            tagDataItem =  h5Item([str('data')+str(c)]) 
            dt = i.attrs['dt']
            data = i.data 
            tagDataItem.data = data[int(startTime/dt):int(endTime/dt)]
            tagDataItem.attrs = i.attrs
            tagItem.addChild(tagDataItem)
            c+=1

    def set_defaultValues(self):
        self.eventBaseline.setText('2000')
        self.eventDuration.setText('4000')



