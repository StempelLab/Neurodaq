from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg

class plotWidget(pg.PlotWidget):

    """ Reimplement Pyqtgraph PlotWidget
    """
    eventSelected = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        pg.PlotWidget.__init__(self, *args, **kwargs)
        self.plotItem = self.getPlotItem()
        self.plotDataItems = []        
        self.viewBox = self.plotItem.getViewBox()
        self.D = False
        self.events = False
        self.eventOnsets = []
        self.currentEvent = 0
        
    def keyPressEvent(self, event):
        """ Specify some key press events.
        """
        super(pg.PlotWidget, self).keyPressEvent(event)
        modifiers = QtWidgets.QApplication.keyboardModifiers()    
        
        # Zoom    
        if (event.key()==QtCore.Qt.Key_Right) and (modifiers==QtCore.Qt.ShiftModifier):
            self.viewBox.scaleBy(x=0.5, y=1)       
        elif (event.key()==QtCore.Qt.Key_Left) and (modifiers==QtCore.Qt.ShiftModifier):
            self.viewBox.scaleBy(x=2, y=1) 
        elif (event.key()==QtCore.Qt.Key_Up) and (modifiers==QtCore.Qt.ShiftModifier):
            self.viewBox.scaleBy(x=1, y=0.5)  
        elif (event.key()==QtCore.Qt.Key_Down) and (modifiers==QtCore.Qt.ShiftModifier):
            self.viewBox.scaleBy(x=1, y=2)  
        # Event browse
        elif (event.key()==QtCore.Qt.Key_Right) and (self.events==True):
            if self.currentEvent<len(self.eventOnsets):
                self.currentEvent += 1 
                xRange = self.viewBox.viewRange()[0][1]-self.viewBox.viewRange()[0][0]
                self.viewBox.setXRange(self.eventOnsets[self.currentEvent]-xRange/2.,
                                       self.eventOnsets[self.currentEvent]+xRange/2., padding=0)              
                self.emit(QtCore.SIGNAL('eventSelected'))                            
        elif (event.key()==QtCore.Qt.Key_Left) and (self.events==True):
            if self.currentEvent>0:
                self.currentEvent -= 1    
                xRange = self.viewBox.viewRange()[0][1]-self.viewBox.viewRange()[0][0]
                self.viewBox.setXRange(self.eventOnsets[self.currentEvent]-xRange/2.,
                                       self.eventOnsets[self.currentEvent]+xRange/2., padding=0)                      
                self.emit(QtCore.SIGNAL('eventSelected'))
        # Pan                                       
        elif event.key() == QtCore.Qt.Key_Right:        
            xRange = self.viewBox.viewRange()[0][1]-self.viewBox.viewRange()[0][0]
            self.viewBox.setXRange(self.viewBox.viewRange()[0][0]+xRange, self.viewBox.viewRange()[0][1]+xRange)
        elif event.key() == QtCore.Qt.Key_Left:        
            xRange = self.viewBox.viewRange()[0][1]-self.viewBox.viewRange()[0][0]
            self.viewBox.setXRange(self.viewBox.viewRange()[0][0]-xRange, self.viewBox.viewRange()[0][1]-xRange)
        elif event.key() == QtCore.Qt.Key_Down:
            yRange = (self.viewBox.viewRange()[1][1]-self.viewBox.viewRange()[1][0])/4.0
            self.viewBox.setYRange(self.viewBox.viewRange()[1][0]+yRange, self.viewBox.viewRange()[1][1]+yRange)
        elif event.key() == QtCore.Qt.Key_Up:
            yRange = (self.viewBox.viewRange()[1][1]-self.viewBox.viewRange()[1][0])/4.0
            self.viewBox.setYRange(self.viewBox.viewRange()[1][0]-yRange, self.viewBox.viewRange()[1][1]-yRange)
        # Additional modifiers for mouse events
        #elif event.key() == QtCore.Qt.Key_D:
        #    self.D = True

    def keyReleaseEvent(self, event):
        """ Specify some key release events, mainly key presses used as mouse modifiers
        """
        super(pg.PlotWidget, self).keyReleaseEvent(event)
        if event.key() == QtCore.Qt.Key_D:
            self.D = False    
            #print('key release')

    def mousePressEvent(self, event):
        super(pg.PlotWidget, self).mousePressEvent(event)
        modifiers = QtWidgets.QApplication.keyboardModifiers()   
        if (event.button()==QtCore.Qt.LeftButton) and self.D==True: #(modifiers==QtCore.Qt.ShiftModifier):
            pos = self.plotItem.vb.mapDeviceToView(pg.QtCore.QPointF(event.pos()))
            #self.addLine(x=pos.x())
            #self.addLine(y=pos.y())
            print(pos.x(), pos.y())
                                            
