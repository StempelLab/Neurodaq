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
        self.entryName = 'Get Protocol Data Dom'
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
        self.eventsBox = QtWidgets.QCheckBox('Get events')
        self.toolOptions.append([self.eventsBox])
        self.eventBaseline = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Baseline'), self.eventBaseline])
        self.eventDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Duration'), self.eventDuration])
        ############################################

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """Process stimulation protocols from visual and pulse stimulation.
        Creates new tree items for each protocol and the corresponding frame number,
        plus a tree item for non-triggers. If protocol data already exists from
        previous runs, it appends data to the frame items.

        Use by selecting the item holding children with Protocol Names and Indices

        NEW NOTE: baseline and duration in ms, to be able to get events from inputs
        with different dt. This means it will not work properly if dt is not correct
        in the 'Indices' item (and everywhere else..), so can't be lazy...

        Options:
        1) get event
        """


        ############################################
        # ANALYSIS FUNCTION

        # Read options
        self.baseline = int(self.eventBaseline.text())
        self.duration = int(self.eventDuration.text())

        # Get names and indices from selected parent item
        self.names, self.triggers = [], []
        self.parentItem = browser.ui.workingDataTree.selectedItems()[0]
        for i in range(self.parentItem.childCount()):
            item = self.parentItem.child(i)
            if 'Names' in item.text(0):
               self.names = re.findall(r"'(.*?)'", item.data, re.DOTALL)
            elif 'Indices' in item.text(0):
               self.triggers = item.data
               self.triggersDt = item.attrs['dt']
        if len(self.names)==0 or len(self.triggers)==0:
            aux.warning_box('Protocol details not found',
                            infoText='Using trigger levels only')
            self.noProtocolNames()
        else:
            self.withProtocolNames()

        ############################################
    def withProtocolNames(self):
        # Get trigger times (in data points)
        tarray = np.arange(0, len(self.triggers))
        self.tevents = tarray[self.triggers>0.5]  # 0.5 is to get rid of noise

        # Iterate names and add entries to data tree
        protocols = list(set(self.names))
        inames = list(enumerate(self.names))

        # Get some events variables started
        if self.eventsBox.isChecked():
            pathsList = aux.selectItem_box(self.browser)
            itemPaths = [i.split('/') for i in pathsList] # itemPath.split('/')
            root = self.browser.ui.workingDataTree.invisibleRootItem()
            dataSourceItems = []
            for path in itemPaths:
                sourceItem = aux.getItemFromPath(path, root, level=0)
                dataSourceItems.append(sourceItem)
                if ('video' in sourceItem.attrs) and (sourceItem.attrs['video']=='True'):
                    self.clip = VideoFileClip(self.browser.currentFolder+'/'+sourceItem.attrs['mrl'])

        # Additional runs
        protocolsItem = aux.getChild(self.parentItem, 'protocols_data')
        if protocolsItem:
            for protocol in protocols:
                item = aux.getChild(protocolsItem, str(protocol))
                for i in inames:
                    if i[1] == protocol:
                        triggerFrame = self.tevents[i[0]]
                        if int(self.triggers[triggerFrame])==1:
                            itemTriggers = aux.getChild(item, 'non_triggers')
                        elif int(self.triggers[triggerFrame])==3:
                            itemTriggers = aux.getChild(item, 'triggers')
                        elif int(self.triggers[triggerFrame])==2:
                            itemTriggers = aux.getChild(item, 'manual')
                        elif int(self.triggers[triggerFrame])==4:
                            itemTriggers = aux.getChild(item, 'homing') 
                        elif int(self.triggers[triggerFrame])==5:
                            itemTriggers = aux.getChild(item, 'control')   
                        if itemTriggers:
                            frameItem = aux.getChild(itemTriggers, 'frame_'+str(triggerFrame))
                        else:
                            frameItem = None
                        if self.eventsBox.isChecked():
                            for sourceItem in dataSourceItems:
                                child = h5Item([str(sourceItem.text(0))])
                                self.getEvent(child, sourceItem, triggerFrame)
                                frameItem.addChild(child)
        # First run
        else:
            protocolsItem = h5Item([str('protocols_data')])
            self.parentItem.addChild(protocolsItem)
            for protocol in protocols:
                #print(protocol)
                item = h5Item([str(protocol)])
                item_triggers = h5Item([str('triggers')])
                item_nontriggers = h5Item([str('non_triggers')])
                item_manualtriggers = h5Item([str('manual')])
                item_homingtriggers = h5Item([str('homing')])
                item_controltriggers = h5Item([str('control')])
                item.addChild(item_triggers)
                item.addChild(item_nontriggers)
                item.addChild(item_manualtriggers)
                item.addChild(item_controltriggers)
                item.addChild(item_homingtriggers)
                for i in inames:
                    if i[1] == protocol:
                        triggerFrame = self.tevents[i[0]]
                        frameItem = h5Item(['frame_'+str(triggerFrame)])
                        if self.eventsBox.isChecked():
                            for sourceItem in dataSourceItems:
                                child = h5Item([str(sourceItem.text(0))])
                                self.getEvent(child, sourceItem, triggerFrame)
                                frameItem.addChild(child)
                        if int(self.triggers[triggerFrame])==1:
                            item_nontriggers.addChild(frameItem)
                        elif int(self.triggers[triggerFrame])==3:
                            item_triggers.addChild(frameItem)
                        elif int(self.triggers[triggerFrame])==2:
                            item_manualtriggers.addChild(frameItem)
                        elif int(self.triggers[triggerFrame])==4:
                            item_homingtriggers.addChild(frameItem)
                        elif int(self.triggers[triggerFrame])==5:
                            item_controltriggers.addChild(frameItem)
                protocolsItem.addChild(item)

    def noProtocolNames(self):
        # Get trigger times (in data points)
        tarray = np.arange(0, len(self.triggers))
        self.tevents = tarray[self.triggers>0.5]

        # Get some events variables started
        if self.eventsBox.isChecked():
            pathsList = aux.selectItem_box(self.browser)
            itemPaths = [i.split('/') for i in pathsList] # itemPath.split('/')
            root = self.browser.ui.workingDataTree.invisibleRootItem()
            dataSourceItems = []
            for path in itemPaths:
                sourceItem = aux.getItemFromPath(path, root, level=0)
                dataSourceItems.append(sourceItem)
                if ('video' in sourceItem.attrs) and (sourceItem.attrs['video']=='True'):
                    self.clip = VideoFileClip(self.browser.currentFolder+'/'+sourceItem.attrs['mrl'])


        # Additional runs
        protocolsItem = aux.getChild(self.parentItem, 'protocols_data')
        if protocolsItem:
            for t in self.tevents:
                triggerFrame = t
                if int(self.triggers[triggerFrame])==1:
                    itemTriggers = aux.getChild(protocolsItem, 'non_triggers')
                elif int(self.triggers[triggerFrame])==3:
                    itemTriggers = aux.getChild(protocolsItem, 'triggers')
                elif int(self.triggers[triggerFrame])==2:
                    itemTriggers = aux.getChild(protocolsItem, 'manual')
                elif int(self.triggers[triggerFrame])==4:
                    itemTriggers = aux.getChild(protocolsItem, 'homing') 
                elif int(self.triggers[triggerFrame])==5:
                    itemTriggers = aux.getChild(protocolsItem, 'control')   
                if itemTriggers:
                    frameItem = aux.getChild(itemTriggers, 'frame_'+str(triggerFrame))
                else:
                    frameItem = None
                if self.eventsBox.isChecked():
                    for sourceItem in dataSourceItems:
                        child = h5Item([str(sourceItem.text(0))])
                        self.getEvent(child, sourceItem, triggerFrame)
                        frameItem.addChild(child)


        # First run
        else:
            protocolsItem = h5Item([str('protocols_data')])
            self.parentItem.addChild(protocolsItem)
            item_triggers = h5Item([str('triggers')])
            item_nontriggers = h5Item([str('non_triggers')])
            item_manualtriggers = h5Item([str('manual')])
            item_homingtriggers = h5Item([str('homing')])
            item_controltriggers = h5Item([str('control')])
            protocolsItem.addChild(item_triggers)
            protocolsItem.addChild(item_nontriggers)
            protocolsItem.addChild(item_manualtriggers)
            protocolsItem.addChild(item_controltriggers)
            protocolsItem.addChild(item_homingtriggers)
            for t in self.tevents:
                triggerFrame = t
                frameItem = h5Item(['frame_'+str(triggerFrame)])
                if self.eventsBox.isChecked():
                    for sourceItem in dataSourceItems:
                        child = h5Item([str(sourceItem.text(0))])
                        self.getEvent(child, sourceItem, triggerFrame)
                        frameItem.addChild(child)
                if int(self.triggers[triggerFrame])==1:
                    item_nontriggers.addChild(frameItem)
                elif int(self.triggers[triggerFrame])==3:
                    item_triggers.addChild(frameItem)
                elif int(self.triggers[triggerFrame])==2:
                    item_manualtriggers.addChild(frameItem)
                elif int(self.triggers[triggerFrame])==4:
                    item_homingtriggers.addChild(frameItem)
                elif int(self.triggers[triggerFrame])==5:
                    item_controltriggers.addChild(frameItem)



    def makeVideoStream(self, subclip, item):
        fpath = os.path.split(self.browser.currentSaveFile)
        fdir = fpath[0]
        folder = '.'+os.path.splitext(fpath[1])[0]
        if folder not in os.listdir(fdir):
             os.mkdir(folder)
        savename = fdir+folder+str(item.text(0))+'.mp4'
        subclip.write_videofile(savename, fps=subclip.fps)
        item.attrs['video'] = 'True'
        item.attrs['mrl'] = savename

    def getEvent(self, child, dataSourceItem, triggerFrame):
        triggerTime = triggerFrame*self.triggersDt
        dt = dataSourceItem.attrs['dt']
        startTime = triggerTime-self.baseline
        endTime = triggerTime+self.duration
        #print(child.text(0), triggerTime, startTime, endTime)
        if ('video' in dataSourceItem.attrs) and (dataSourceItem.attrs['video']=='True'):
            child.attrs['video'] = 'True'
            child.attrs['mrl'] = dataSourceItem.attrs['mrl']
            child.attrs['subclip'] = 'True'
            #child.attrs['tstart'] = (triggerFrame-self.baseline)/self.clip.fps*1000.
            #child.attrs['tstop'] = (triggerFrame+self.duration)/self.clip.fps*1000.
            child.setText = 'clip_'+str(child.text(0))
        else:
            child.data = dataSourceItem.data[int(startTime/dt):int(endTime/dt)]
            child.setText = str(dataSourceItem.text(0))+'_'+str(child.text(0))
            child.attrs['dt'] = dataSourceItem.attrs['dt']
        child.attrs['tstart'] = startTime
        child.attrs['tstop'] = endTime
        child.attrs['triggerTime'] = triggerTime-startTime


    def set_defaultValues(self):
        self.eventBaseline.setText('10000')
        self.eventDuration.setText('60000')
