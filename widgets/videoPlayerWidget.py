import sys
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QVBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg

from .plotWidgets import plotWidget
from .simpleVideoPlayerWidget import simpleVideoPlayerWidget

# sys.path.append(os.path.join(os.path.dirname(__file__), 'widgets'))
# from graphicsWidget import GraphicsWidget
# from plotWidgets import plotWidget
# from NeuroWidget import NeuroWidget
# from simpleVideoPlayerWidget import simpleVideoPlayerWidget
 
class videoPlayerWidget(QWidget):
    moveForwardKeyPress = pyqtSignal()
    moveBackKeyPress = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.players = []
        self.filename = None
        self.xmax = None
        self.nframes = None
        self.fps = None
        
        self.layout = QVBoxLayout(self)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.verticalsplitter = QSplitter(self)
        self.verticalsplitter.setOrientation(QtCore.Qt.Vertical)
        self.layout.addWidget(self.verticalsplitter)
        
        #PlotsWidget
        self.plotsWidget = plotWidget(background='#ECEDEB')
        self.plotsWidget.getAxis('bottom').setPen('k')
        self.plotsWidget.getAxis('left').setPen('k')
        self.plotsWidget.showGrid(x=True, y=True, alpha=0.3)
        self.plotsWidget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred))
        # video cursor
        self.plotsWidget.cursor = True
        self.plotsWidget.cursor1 = pg.InfiniteLine(angle=90, movable=True, pen=pg.mkPen('#2AB825', width=2,))
        self.plotsWidget.addItem(self.plotsWidget.cursor1)
        self.plot_cursor_connection = self.plotsWidget.cursor1.sigPositionChanged.connect(self.cursorMoved)
        # tag cursor
        self.plotsWidget.tagCursorOn = False
        
        self.verticalsplitter.addWidget(self.plotsWidget)
        self.setLayout(self.layout)
        
    def OpenFile(self):
        for player in self.players:
            filename = player.media.get_mrl().replace('file://', '')
            
            if filename == self.filename:
                print("Video already loaded in player - not opening again")
                return        

        player = simpleVideoPlayerWidget()
        self.players.append(player)
        player.OpenFile(self.filename)

        # Get the highes number of frames and fps from all players        
        self.nframes = max(player.nframes for player in self.players)
        self.fps = max(player.fps for player in self.players)
       
        # Connect all player signals
        player.sync_slider_connection = player.PositionSlider.sliderMoved.connect(lambda position, p=player: self.sync_sliders(position, p))
        player.sync_play_pause_connection = player.PlayButton.clicked.connect(lambda _, p=player: self.sync_play_pause(p))
        
        self.moveForwardKeyPress.connect(player.moveForward)
        self.moveBackKeyPress.connect(player.moveBack)
        
        self.moveForwardKeyPress.connect(self.updateUi)
        self.moveBackKeyPress.connect(self.updateUi)

        # Connect the first player UI update to plotWidget
        player.sync_timer_connection = self.players[0].timer.timeout.connect(self.updateUi)

        # Pause player if not paused yet        
        for player in self.players:
            if player.is_paused:
                player.playPause()
        
        # Add the player to the layout
        self.verticalsplitter.addWidget(player)
            
        # Move plot widget to the bottom
        self.plotsWidget.setParent(None)
        self.verticalsplitter.addWidget(self.plotsWidget)

        # Distribute equally
        self.verticalsplitter.setSizes([1] * self.verticalsplitter.count())

    def sync_sliders(self, position, emitting_player):
        """Synchronize all sliders and media players to the given position, except the moved one."""
        for player in self.players:
            if player != emitting_player:
                player.PositionSlider.setValue(position)
                player.setPosition() #As sliderMoved is only triggered when slider is moved and not on value change
                
        # Move the cursor in plotsWidget
        if self.xmax is not None:
            pos = float(position)/1000 * self.xmax
            self.plotsWidget.cursor1.setValue(pos)
                
    def sync_play_pause(self, emitting_player):
        """Synchronize play/pause state across all media players except the clicked one."""
        for player in self.players:
            if player != emitting_player:
                player.PlayButton.clicked.disconnect(player.sync_play_pause_connection)
                player.PlayButton.click()
                player.sync_play_pause_connection = player.PlayButton.clicked.connect(lambda _, p=player: self.sync_play_pause(p))

    def updateUi(self):
        # Move the cursor in plotsWidget
        if self.xmax is not None:
            self.plotsWidget.cursor1.sigPositionChanged.disconnect(self.plot_cursor_connection)
            firstPlayer = self.players[0]
            frame_index = int(firstPlayer.mediaplayer.get_time() / 1000  * firstPlayer.fps)
            pos = float(frame_index)/firstPlayer.nframes * self.xmax
            self.plotsWidget.cursor1.setValue(pos)
            self.plot_cursor_connection = self.plotsWidget.cursor1.sigPositionChanged.connect(self.cursorMoved)

    def cursorMoved(self):
        """Set video slider to the cursor position
        """
        if self.xmax is not None and len(self.players) > 0:
            xpos = self.plotsWidget.cursor1.getXPos()
            position = xpos/self.xmax
            for player in self.players:
                player.PositionSlider.setValue(int(position*1000))
                player.setPosition() #As sliderMoved is only triggered when slider is moved and not on value change

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
                    if dt==1: pos=(pos/1000.)*self.fps # convert to frames
                else:
                    pos=(pos/1000.)*self.fps # convert to frames
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

def main():
    app = QApplication(sys.argv)
    
    # Create a main window with synchronized video players
    mainWindow = videoPlayerWidget()
    mainWindow.filename = '/home/kretschmerf/data/neurodaq_forFritz/19JUN18_BO124p1_ichloc_t2.cam1.mp4'
    mainWindow.OpenFile()
    mainWindow.OpenFile()
    mainWindow.OpenFile()
    mainWindow.show()
    
    # Execute the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()