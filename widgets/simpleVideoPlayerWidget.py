import sys
import os
import time
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget, QGraphicsVideoItem
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QFrame, QWidget, QGridLayout
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal
import pyqtgraph as pg
import vlc
import platform

class simpleVideoPlayerWidget(QtWidgets.QWidget):
    """A simple Media Player using Phonon

    Moviepy is used to read some video properties
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)

        vlc_args = ["--no-xlib", "--vout=opengl"]
        # Create a basic vlc instance
        self.instance = vlc.Instance(vlc_args)

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.is_paused = False
        self.nframes = None
        self.fps = None

        """Set up the user interface, signals & slots
        """
        # Video
        self.videoWidget = QWidget()
        """Set up the user interface, signals & slots"""
        # Create a QWidget for video output
        self.videoOutputWidget = QWidget(self)
        self.videoOutputWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.PlayButton = QPushButton("Play", self)
        self.PlayButton.clicked.connect(self.playPause)

        self.PositionSlider = QSlider(QtCore.Qt.Horizontal, self)
        self.PositionSlider.setToolTip("Position")
        self.PositionSlider.setMaximum(1000)
        self.PositionSlider.sliderMoved.connect(self.setPosition)

        self.status = QLabel(self)
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
        self.timer.timeout.connect(self.updateUi)
        
        self.gridLayout =  QGridLayout(self)
        self.gridLayout.addWidget(self.videoWidget)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setColumnStretch(0, 1)
        
    def playPause(self):
            """Toggle play/pause status
            """
            if self.mediaplayer.is_playing():
                self.mediaplayer.pause()
                self.PlayButton.setText("Play")
                self.is_paused = True
                self.timer.stop()
            else:
                self.mediaplayer.play()
                self.PlayButton.setText("Pause")
                self.timer.start()
                self.is_paused = False
                
    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.PlayButton.setText("Play")

    def OpenFile(self, filename):
        self.media = self.instance.media_new(filename)
        self.media.parse_with_options(1,0)
        while True:
            if str(self.media.get_parsed_status()) == 'MediaParsedStatus.done':
                break #Might be a good idea to add a failsafe in here.
        self.mediaplayer.set_media(self.media)
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

        self.fps = self.mediaplayer.get_fps()
        self.nframes = int(self.media.get_duration()/1000 * self.fps)
            
        self.playPause()

    def setPosition(self):
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

    def updateUi(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.PositionSlider.setValue(media_pos)

        # Update status text
        time_in_seconds = self.mediaplayer.get_time()/1000
        h = int(time_in_seconds // 3600)
        m = int((time_in_seconds % 3600) // 60)
        s = int(time_in_seconds % 60)
        self.status.setText('%02d:%02d:%02d' % (h, m, s))

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def moveForward(self):
        """ Move forward one frame
        """
        if self.mediaplayer.get_state() == vlc.State.Paused:
            self.mediaplayer.next_frame()
            self.updateUi()

    def moveBack(self):
        """ Move back one frame
        """
        if self.mediaplayer.get_state() == vlc.State.Paused:
            current_time = self.mediaplayer.get_time()
            previous_time = current_time - int(1000 / self.fps)
            if previous_time < 0:
                previous_time = 0
            self.mediaplayer.set_time(previous_time)
            self.updateUi()