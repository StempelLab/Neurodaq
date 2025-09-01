import sys
import os
#import user
import time
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFrame
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from widgets import *
from analysis import auxfuncs as aux
import pyqtgraph as pg
from moviepy.editor import *
from widgets.graphicsWidget import GraphicsWidget
import vlc
import platform

class videoPlayerWidget(QtWidgets.QWidget):
    """A simple Media Player using Phonon

    Moviepy is used to read some video properties
    """

    moveForwardKeyPress = pyqtSignal()
    moveBackKeyPress = pyqtSignal()

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)


        vlc_args = ["--no-xlib", "--vout=opengl"]
        # Create a basic vlc instance
        self.instance = vlc.Instance(vlc_args)

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.is_paused = False

        self.createVideoUI()
        self.createPlotUI()
        self.createLayout()
        self.isPaused = False
        self.subclip = False
        self.subclipStart = None
        self.subclipStop = None
        self.xmax = None
        self.nframes = None
        self.clip = None
        
        # Set up event manager
        #self.event_manager = self.player.event_manager()
        #self.event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.on_position_changed)
        # self.event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.on_playing_state)
        # self.event_manager.event_attach(vlc.EventType.MediaPlayerPaused, self.on_paused_state)
        # self.event_manager.event_attach(vlc.EventType.MediaPlayerStopped, self.on_stopped_state)
        
        #self.player.event_manager().event_attach(vlc.EventType.MediaPlayerStateChanged, self.state_changed)

    def on_playing_state(self, event):
        self.play_pause.setText("Pause")
    
    def on_paused_state(self, event):
        self.play_pause.setText("Play")
    
    def on_stopped_state(self, event):
        self.play_pause.setText("Play")
        
    def on_state_changed(self, event):
        # This method will be called whenever the state changes
        state = self.player.get_state()
        print("State changed:", state)
        # Call your state change handling function here
        self.stateChanged(state)
        
    def createLayout(self):
        # Splitter
        self.gridLayout =  QtWidgets.QGridLayout(self)
        self.verticalsplitter = QtWidgets.QSplitter(self)
        self.verticalsplitter.setOrientation(QtCore.Qt.Vertical)
        self.gridLayout.addWidget(self.verticalsplitter, 0, 0, 1, 1)

        # Add widgets
        self.verticalsplitter.addWidget(self.videoWidget)
        #self.verticalsplitter.addWidget(self.plotsWidget)
        self.verticalsplitter.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred))
        self.verticalsplitter.setSizes([1,1])

    def createPlotUI(self):
        self.plotsWidget = plotWidget(background='#ECEDEB')
        self.plotsWidget.getAxis('bottom').setPen('k')
        self.plotsWidget.getAxis('left').setPen('k')
        self.plotsWidget.showGrid(x=True, y=True, alpha=0.3)
        self.plotsWidget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred))
        # video cursor
        self.plotsWidget.cursor = True
        self.plotsWidget.cursor1 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#2AB825', width=2,))
        self.plotsWidget.addItem(self.plotsWidget.cursor1)
        self.plotsWidget.cursor1.sigPositionChanged.connect(self.cursorMoved)
        # tag cursor
        self.plotsWidget.tagCursorOn = False
        #self.plotsWidget.tagCursor = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#FC6B03', width=2,))


        #self.plotsWidget.test = pg.PlotCurveItem(np.ones(100)*1, np.arange(-50,50), clickable=True,
        #                         pen=pg.mkPen('#FC6B03'))
        #self.plotsWidget.addItem(self.plotsWidget.test)
        #self.plotsWidget.testSelected = False

    def createVideoUI(self):
        """Set up the user interface, signals & slots
        """
        # Video
        self.videoWidget = NeuroWidget(0,0)
        """Set up the user interface, signals & slots"""
        # Create a QWidget for video output
        self.videoOutputWidget = QtWidgets.QWidget(self) #QFrame(self)
        self.videoOutputWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #self.videoOutputWidget.setFrameShape(QFrame.Box) 

        self.PlayButton = QtWidgets.QPushButton("Play", self)
        self.PlayButton.clicked.connect(self.play_pause)

        self.PositionSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.PositionSlider.setToolTip("Position")
        self.PositionSlider.setMaximum(1000)
        self.PositionSlider.valueChanged.connect(self.set_position)

        #self.brightnessSlider = QtWidgets.QSlider(QtCore.Qt.Vertical, self)
        #self.brightnessSlider.setToolTip('Brightness')
        #self.brightnessSlider.sliderMoved.connect(self.setBrightness)

        #self.contrastSlider = QtWidgets.QSlider(QtCore.Qt.Vertical, self)
        #self.contrastSlider.setToolTip('Contrast')
        #self.contrastSlider.sliderMoved.connect(self.setContrast)

        self.moveForwardKeyPress.connect(self.moveForward)
        self.moveBackKeyPress.connect(self.moveBack)

        self.status = QtWidgets.QLabel(self)
        self.status.setAlignment(QtCore.Qt.AlignRight |
            QtCore.Qt.AlignVCenter)

        self.VBoxLayout = QVBoxLayout(self.videoWidget)
        self.VBoxLayout.addWidget(self.videoOutputWidget)
        
        
        self.HButtonBox = QHBoxLayout()
        self.HButtonBox.addWidget(self.PlayButton)
        self.HButtonBox.addWidget(self.PositionSlider)
        self.HButtonBox.addWidget(self.status)
        self.VBoxLayout.addLayout(self.HButtonBox)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def play_pause(self):
            """Toggle play/pause status
            """
            if self.mediaplayer.is_playing():
                self.mediaplayer.pause()
                self.PlayButton.setText("Play")
                self.is_paused = True
                self.timer.stop()
            else:
                # if self.mediaplayer.play() == -1:
                #     self.open_file()
                #     return

                self.mediaplayer.play()
                self.PlayButton.setText("Pause")
                self.timer.start()
                self.is_paused = False
                
    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.PlayButton.setText("Play")


    def OpenFile(self):
        self.clip = VideoFileClip(self.filename)
        media = self.instance.media_new(self.filename)
        
        self.mediaplayer.set_media(media)
        self.status.setText('%02d:%02d:%02d' % (0, 0, 0))
        
        # Assuming self.videoWidget is your video display widget
        window_id = int(self.videoOutputWidget.winId())
        
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux": # for Linux using the X Server
            self.mediaplayer.set_xwindow(window_id)
        elif platform.system() == "Windows": # for Windows
            self.mediaplayer.set_hwnd(window_id)
        elif platform.system() == "Darwin": # for MacOS
            self.mediaplayer.set_nsobject(window_id)

        if self.subclip:
            self.makeSeekable()
            self.mediaplayer.set_time(self.subclipStart)
            self.nframes = int((self.subclipStop - self.subclipStart) / 1000. * self.clip.fps)
        else:
            self.nframes = int(self.clip.duration * self.clip.fps)
           
        self.play_pause()
             
        frame_index = int(self.mediaplayer.get_time() / 1000  * self.clip.fps)
        self.plotsWidget.cursor1.setValue(frame_index) #TODO

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.PositionSlider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.PositionSlider.setValue(media_pos)

        time_in_seconds = media_pos/self.clip.fps
        h = int(time_in_seconds // 3600)
        m = int((time_in_seconds % 3600) // 60)
        s = int(time_in_seconds % 60)

        self.status.setText('%02d:%02d:%02d' % (h, m, s))

        # Move the cursor in plotsWidget
        if self.xmax is not None:
            frame_index = int(self.mediaplayer.get_time() / 1000  * self.clip.fps)
            pos = float(frame_index)/self.nframes * self.xmax
            self.plotsWidget.cursor1.setValue(pos)
        #else:
        #    self.plotsWidget.cursor1.setValue(Position)


        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()


    def cursorMoved(self):
        """Set video slider to the cursor position
        """
        # xpos = self.plotsWidget.cursor1.getXPos()
        # if self.xmax is not None:
        #     pos = xpos/self.xmax
        #     self.PositionSlider.setValue(int(float(pos)*self.nframes))
        #     if not self.player.isPlaying():
        #         if self.subclip:
        #             self.player.setPosition(float(pos*(self.subclipStop-self.subclipStart)+self.subclipStart))
        #         else:
        #             self.player.setPosition(float(pos*self.player.mediaObject().totalTime()))

    def setBrightness(self, Position):
        """ Set the video brightness
        """
        print('not ported yet')
        #self.player.videoWidget().setBrightness(Position/100.)

    def setContrast(self, Position):
        """ Set the video contrast
        """
        print('not ported yet')
        #self.player.videoWidget().setContrast(Position/100.)

    def moveForward(self):
        """ Move forward one frame
        """
        if self.mediaplayer.get_state() == vlc.State.Paused:
            self.mediaplayer.next_frame()
            self.update_ui()
        #     if self.subclip:
        #         self.updateUI(t-self.subclipStart)
        #     else:
        #         self.updateUI(t)

    def moveBack(self):
        """ Move back one frame
        """
        if self.mediaplayer.get_state() == vlc.State.Paused:
            current_time = self.mediaplayer.get_time()
            previous_time = current_time - int(1000 / self.clip.fps)
            if previous_time < 0:
                previous_time = 0
            self.mediaplayer.set_time(previous_time)
            self.update_ui()
            # if self.subclip:
            #     self.updateUI(t-self.subclipStart)
            # else:
            #     self.updateUI(t)
                
    # def updateUI(self, time):
    #     """ Updates items in the user interface
    #     """
    #     self.PositionSlider.setValue(int((time/1000.) * self.media.get_fps()))
    #     if self.xmax is not None:
    #         if self.subclip:
    #             pos = float(time)/(self.subclipStop-self.subclipStart)*self.xmax
    #         else:
    #             pos = float(time)/self.player.mediaObject().totalTime()*self.xmax
    #         self.plotsWidget.cursor1.setValue(int(pos))
           
    #     # Update timer
    #     time = int(time) / 1000
    #     h = int(time // 3600)
    #     m = int((time % 3600) // 60)
    #     s = time % 60
        
    #     self.status.setText('%02d:%02d:%02d'%(h,m,s))

    def keyPressEvent(self, event):
        """ Specify some key press events.
        """
        super(videoPlayerWidget, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Right:
            self.moveForwardKeyPress.emit()
        elif event.key() == QtCore.Qt.Key_Left:
            self.moveBackKeyPress.emit()

    def writeTag(self, browser, item, tag):
        """ Write user selected tag to the stream item as
        an attribute (tag_X: frame time in ms)
        """
        if ('video' in item.attrs) and (item.attrs['video']=='True'):
            currentTime = self.player.currentTime()
            if self.subclip: currentTime = currentTime - self.subclipStart
            if tag in item.attrs:
                if not isinstance(item.attrs[tag], list):    # hack, list gets converted to array when saved
                    item.attrs[tag] = list(item.attrs[tag])  # don't know when/where..
                item.attrs[tag].append(currentTime)
            else:
                item.attrs[tag] = [currentTime]
            self.showTag(item, tag)
            browser.ui.actionShowVideoTags.setChecked(True)
            print(tag, ':', currentTime)
        else:
            aux.error_box('Selected item is not a video stream')

    def toggleTag(self, item, tag, checked):
        """ Toggle tag cursor on and off
        """
        if checked:
            print('showing tag')
            self.showTag(item, tag)
        else:
            for t in self.tagCurveItems: self.plotsWidget.removeItem(t)
            self.plotsWidget.tagCursorOn = False
            self.tagCurveItems = []

    def showTag(self, item, tag):
        """ Show a cursor at the time of the selected tag in the video plots window.
        If dt of the plotted items is 1 it assumes it is in frames, otherwise assumes time.
        """
        if self.plotsWidget.tagCursorOn==True:
            for t in self.tagCurveItems: self.plotsWidget.removeItem(t)
            self.tagCurveItems = []
        if tag in item.attrs:
            self.tagCurveItems = []
            for t in item.attrs[tag]:
                pos = float(t) # in ms
                if self.plotsWidget.plotDataItems:
                    dt = self.plotsWidget.plotDataItems[0].attrs['dt']
                    if dt==1: pos=(pos/1000.)*self.clip.fps # convert to frames
                else:
                    pos=(pos/1000.)*self.clip.fps # convert to frames
                #if self.plotsWidget.tagCursorOn==False:
                curveItem = pg.PlotCurveItem(np.ones(100)*pos, np.arange(-50,50), clickable=True,
                            pen=pg.mkPen('#FC6B03'))
                curveItem.sigClicked.connect(self.selectTag)
                curveItem.selected = False
                self.plotsWidget.addItem(curveItem)
                self.tagCurveItems.append(curveItem)
                self.plotsWidget.tagCursorOn = True

    def selectTag(self, event):
        if event.selected==False:
            event.setShadowPen(pg.mkPen('#FCD302', width=5))
            event.selected=True
        else:
            event.setShadowPen(pg.mkPen(None))
            event.selected=False

    def clearAllTags(self, item, tag):
        if ('video' in item.attrs) and (item.attrs['video']=='True'):
            item.attrs[tag] = []
        else:
            aux.error_box('Selected item is not a video stream')
        for t in self.tagCurveItems: self.plotsWidget.removeItem(t)
        self.tagCurveItems = []
        self.plotsWidget.tagCursorOn = False

    def clearSelectedTags(self, item, tag):
        if ('video' in item.attrs) and (item.attrs['video']=='True'):
            if not isinstance(item.attrs[tag], list):    # hack, list gets converted to array when saved
                item.attrs[tag] = list(item.attrs[tag])  # don't know when/where..
            c = 0
            indices = []
            for i in self.tagCurveItems:
                if i.selected==True:
                    indices.append(c)
                    self.plotsWidget.removeItem(i)
                c+=1
            for i in sorted(indices, reverse=True):
                del self.tagCurveItems[i]
                del item.attrs[tag][i]
        else:
            aux.error_box('Selected item is not a video stream')
        self.plotsWidget.tagCursorOn = False
