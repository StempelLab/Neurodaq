from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import os
import sip
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
        self.entryName = 'Get Tag Data'
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
        self.triggerTimeBox = QtWidgets.QCheckBox('Get times from trigger')
        self.toolOptions.append([self.triggerTimeBox])
        ############################################
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)


    def func(self, browser):
        """ Extract the time of the tags in all video streams in the tree
        of selected items. Create a new group "tag data" in "frame_xxx" items
        with the results of the analysis.

        Currently it is desinged to be run on the Protocols_Data tree, the
        output of Get Protocol Data

        Outputs:
        - times of all tags that exist, as single tree items


        Options:
        1) Time from trigger (from time of trigger that was used to get the frame item)
        """

        ############################################
        # ANALYSIS FUNCTION

        # Read options

        # Iterate all selected protocols
        for protocolItem in browser.ui.workingDataTree.selectedItems():

            # Iterate Protocol Item (contains the different triggers)
            for c in range(protocolItem.childCount()):
                triggerItem = protocolItem.child(c)

                #Iterate trigger item (contains the frame items)
                for c in range(triggerItem.childCount()):
                    self.getTags(triggerItem.child(c))

        ############################################

    def getTags(self, frameItem, tags=['A','B','C','D','E','F','G','H','I','J',
                                     'K','L','M','N','O','P','Q','R','S','T']):
         """ Finds the video stream item, gets the tags
         and stores the tag times in a new item group
         """
         # Create storage group
         item = aux.getItemFromPath(['TagData'],frameItem)
         if item: sip.delete(item)
         tagDataItem =  h5Item([str('TagData')])
         self.browser.make_nameUnique(frameItem, tagDataItem, tagDataItem.text(0))
         frameItem.addChild(tagDataItem)

         # Get video stream with the tags
         streamItem = aux.getChild(frameItem, 'Video stream')

         # Build list of Tags that exist in video
         videoTags = []
         for tag in tags:
             tagString = "VideoTag_"+tag
             print(frameItem.text(0), streamItem.attrs['mrl'])
             if tagString in streamItem.attrs:
                 videoTags.append(tagString)

         # Iterate through tags and get data out
         tagTimesItem = h5Item([str('TagTimes_absolute')])
         tagDataItem.addChild(tagTimesItem)
         if self.triggerTimeBox.isChecked():
             tagTriggerTimesItem = h5Item([str('TagTimes_fromTrigger')])
             tagDataItem.addChild(tagTriggerTimesItem)

         for tag in videoTags:
             # Get Tag times
             if len(streamItem.attrs[tag])>0: # in case the list is empty
                 tagItem =  h5Item([tag])
                 tagItem.data = streamItem.attrs[tag]
                 tagTimesItem.addChild(tagItem)

                 # Get optional time from trigger
                 if self.triggerTimeBox.isChecked():
                     try:
                         triggerTime = float(streamItem.attrs['triggerTime'])
                         tagItem =  h5Item([tag])
                         tagItem.data = [d - triggerTime for d in streamItem.attrs[tag]]
                         tagTriggerTimesItem.addChild(tagItem)
                     except KeyError:
                         aux.error_box('No trigger times found')
                         return
