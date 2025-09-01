from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import os
import numpy as np
from analysis import auxfuncs as aux
from widgets import h5Item
from ..acq4 import filterfuncs as acq4filter
from moviepy.editor import *
from moviepy.video.tools.drawing import blit
from PIL import Image, ImageDraw
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Export video stream'  
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
        self.format = QtWidgets.QComboBox()
        self.format.addItem('MPEG4')
        self.format.addItem('JPEG frames')
        self.formatLabel = QtWidgets.QLabel('Format')
        self.toolOptions.append([self.formatLabel, self.format])
        self.trackingBox = QtWidgets.QCheckBox('Show tracking')
        self.toolOptions.append([self.trackingBox])
        self.trackingLag = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Lag (frames)'), self.trackingLag])
        self.vectorBox = QtWidgets.QCheckBox('Show vector')
        self.toolOptions.append([self.vectorBox])
        self.vectorLag = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Lag (frames)'), self.vectorLag])
        self.visualBox = QtWidgets.QCheckBox('Draw visual stim')
        self.toolOptions.append([self.visualBox])
        self.visualContrast = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Contrast (%)'), self.visualContrast])
        self.pulseBox = QtWidgets.QCheckBox('Draw pulse stim')
        self.toolOptions.append([self.pulseBox])
        self.pulseDuration = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Duration (frames)'), self.pulseDuration])        
        ############################################        

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Export video subclips to mpeg4 files or individual jpeg frames

        Creates a new file (or folder with all the jpegs) in current save folder, 
        with the name of the subclip parent item (i.e.: frame_number). Life is 
        easier if dt of XY, etc is in frames, so keep them that way. 

        Use by selecing the parent item. 

        Options:
        1) Show tracking with centre of mass and line lagging (set lag, positive is in the past)
        2) Show XY displacement vector (set lag, positive is in the past)
        3) Draw visual stimulus profile
        4) Draw spot to show pulse stimulation onset and duration
        """


        ############################################
        # ANALYSIS FUNCTION      

        # Read options 
        self.trackingLagLen = int(self.trackingLag.text())
        self.vectorLagLen = int(self.vectorLag.text())
        self.visualContrastVal = int(self.visualContrast.text())
        self.formatVal = str(self.format.currentText())
        self.pulseLag = int(self.pulseDuration.text())

        # Get items needed 
        self.parentItem = browser.ui.workingDataTree.selectedItems()[0]
        if self.parentItem:
            for i in range(self.parentItem.childCount()):
                item = self.parentItem.child(i)
                if 'Spot Diameter' in item.text(0):
                    self.visualStim = item
                elif 'Video stream' in item.text(0):
                    self.stream = item
                elif 'X-Vertical' in item.text(0):
                    self.vertical = item
                elif 'Y-Horizontal' in item.text(0):
                    self.horizontal = item
                elif 'Pulse Stimuli Start' in item.text(0):
                    self.pulseStim = item
                    self.pulseLagCounter = 0
        else:
            aux.error_box('No item selected')
            return
        if not hasattr(self, 'stream'):
            aux.error_box('No video stream found')
            return

        # Open video        
        self.clip = VideoFileClip(self.browser.currentFolder+'/'+self.stream.attrs['mrl'] )
        self.start = self.stream.attrs['tstart']/1000.  # sec
        self.stop = self.stream.attrs['tstop']/1000.
        self.duration = self.stop-self.start

        # Write video or frames
        if self.formatVal=='MPEG4':
            savename = self.browser.saveFolder+'/'+self.parentItem.text(0)+'.mp4'
            self.clipOut = VideoClip(self.make_frame, duration=self.duration)
            self.clipOut.write_videofile(savename, fps=self.clip.fps)
        elif self.formatVal=='JPEG frames':
            dirname = self.browser.saveFolder+'/'+self.parentItem.text(0)
            aux.mkdir_p(dirname)
            basename = dirname+'/''frame%03d.jpg'
            self.clipOut = VideoClip(self.make_frame, duration=self.duration)
            self.clipOut.write_images_sequence(basename, fps=self.clip.fps)
        ############################################  

    def start_imageDraw(self, frame):
        """ Draw basic frame to be saved in movie clip
        """
        self.imframe = Image.fromarray(frame)
        self.draw = ImageDraw.Draw(self.imframe, 'RGBA')

    def draw_circle(self, r, x, y, color):
        self.draw.ellipse((x-r,y-r,x+r,y+r), fill=color)        
    
    def draw_trace(self, t, lag, color):
        """ Draw lagging position trace.
        t: current frame time in seconds, from the start of original stream
        lag: number of frames to lag
        """
        currentFrame = t * self.clip.fps 
        if lag-(currentFrame)>0: lag = currentFrame # for while lag is bigger than frames played
        startFrame = currentFrame-lag
        if startFrame<0: startFrame = 0
        linepoints = [(round(self.vertical.data[f]), round(self.horizontal.data[f])) for f in np.arange(startFrame, currentFrame)]
        self.draw.line(linepoints, fill=color)     

    def draw_vector(self, t, lag, color):
        """ Draw displacement vector.
        t: current frame time in seconds, from the start of original stream
        lag: number of frames to lag
        """
        currentFrame = t * self.clip.fps 
        if lag-(currentFrame)>0: lag = currentFrame # for while lag is bigger than frames played
        startFrame = currentFrame-lag
        if startFrame<0: startFrame = 0
        currentVertical = self.vertical.data[currentFrame]
        currentHorizontal = self.horizontal.data[currentFrame]
        linepoints = [(currentVertical, currentHorizontal), (self.vertical.data[startFrame],self.horizontal.data[startFrame])]
        self.draw.line(linepoints, fill=color) 

        x = round(self.vertical.data[currentFrame])
        y = round(self.horizontal.data[currentFrame])
        self.draw_circle(2, x, y, (166,53,204,255))

        x = round(self.vertical.data[startFrame])
        y = round(self.horizontal.data[startFrame])
        self.draw_circle(2, x, y, (66,53,204,255))

    def make_frame(self, t):
        """ Compose frame to be save in movie clip.
        Function is called iteratively by VideoClip
        """
        frameTime = t + self.start
        frameNumber = int(t * self.clip.fps) # for use with data which has the subclip duration
        frame = self.clip.get_frame(frameTime)
        self.start_imageDraw(frame)
        
        # Draw tracking circle and line
        if self.trackingBox.isChecked():    
            x = round(self.vertical.data[frameNumber])
            y = round(self.horizontal.data[frameNumber])
            self.draw_circle(5, x, y, (166,53,204,255))
            self.draw_trace(t, self.trackingLagLen, (166,53,204,255))

        # Draw displacement vector
        if self.vectorBox.isChecked():  
            self.draw_vector(t, self.vectorLagLen, (166,53,204,255))
        
        # Draw looming spot
        if self.visualBox.isChecked(): 
            c = int(self.visualContrastVal/100.*255)
            x, y = 810, 185
            r = self.visualStim.data[frameNumber]
            self.draw_circle(r, x, y, (0,0,0,c))

        # Draw pulse stim spot
        if self.pulseBox.isChecked():
            r = 0
            x, y = 980, 40
            if self.pulseStim.data[frameNumber]==2: 
                self.pulseLagCounter = self.pulseLag  
            if self.pulseLagCounter>0:
                r = 30
                self.pulseLagCounter-=1
            self.draw_circle(r, x, y, (100,149,237,200))        

        return np.array(self.imframe)

    def set_defaultValues(self):
        self.trackingLag.setText('0')
        self.vectorLag.setText('1')
        self.visualContrast.setText('90')


