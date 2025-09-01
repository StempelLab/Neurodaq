""" Functions for plotting using PyQtGraph
"""

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg

def plot_singleData(browser, plotWidget, data):
    """ Plot a single trace.
    """
    plotWidget.clear()
    plotWidget.plot(data, pen=pg.mkPen('#3790CC'))

    
def plot_multipleData(browser, plotWidget, itemList, clear=True, color='#3790CC'):
    """ Plot user-selected traces from the working data tree.

    Store the data indexes of the plotted items for use in 
    data analyis functions.
    
    Store max and min of data and x-axis for zoom out function.
    """
    if clear: 
        plotWidget.clear()
        plotWidget.plotDataIndex, plotWidget.plotDataItems = [], []
        if plotWidget.cursor: replot_cursors(plotWidget) 
    for n, item in enumerate(itemList):
        if item.data is not None:
            try:
                x = item.attrs['timeStamp'] 
            except KeyError:           
                try:
                    dt = item.attrs['dt']
                except KeyError:
                    dt = 1
                x = make_xvector(item.data, dt)     
            y = item.data
            color = pg.intColor(n)
            plotWidget.plot(x, y, pen=color)
            plotWidget.plotDataItems.append(item)

def browse_singleData(browser, plotWidget, currentItem, clear=True, color='#3790CC'):
    """ Plot single trace of currentItem.
    Different from plot_singleData because the source is an item
    instead of the data directly.
    """
    if clear: 
        plotWidget.clear()
        plotWidget.plotDataIndex, plotWidget.plotDataItems = [], []
        if plotWidget.cursor: replot_cursors(plotWidget)   
    if currentItem.data is not None:
        try:
            dt = currentItem.attrs['dt']
        except KeyError:
            dt = 1    
        x = make_xvector(currentItem.data, dt)    
        #x = np.arange(0, len(currentItem.data)*dt, dt)
        y = currentItem.data
        plotWidget.plot(x, y, pen=pg.mkPen(color))        
        plotWidget.plotDataItems.append(currentItem) 

def browse_image(browser, imageWidget, currentItem):
    imageWidget.setImage(currentItem.data)

def replot(browser, plotWidget):
    """ Function to replot the data currently in the data plot tab.
    Useful for visualising the data after any analysis transformation.
    """
    plotWidget.clear()
    if plotWidget.cursor: replot_cursors(plotWidget)
    for item in plotWidget.plotDataItems:  
        try:
            dt = item.attrs['dt']
        except KeyError:
            dt = 1
        #x = np.arange(0, len(item.data)*dt, dt)
        x = make_xvector(item.data, dt) 
        y = item.data
        plotWidget.plot(x, y, pen=pg.mkPen('#3790CC'))
              

def zoom_out(browser, plotWidget):
    """ Zoom out to the X and Y data boundaries.
    """ 
    if plotWidget.xBoundaries:
        plotWidget.setXRange(0, np.max(plotWidget.xBoundaries))
        plotWidget.setYRange(np.min(plotWidget.yBoundaries), np.max(plotWidget.yBoundaries))

def show_cursors(browser, plotWidget):
    """ Show two cursors for use in data analysis.
    """
    axisRange = plotWidget.viewRange()
    x1, x2 = axisRange[0]
    y1, y2 = axisRange[1]
    plotWidget.cursor1Pos = x1+(x2-x1)/2.-(x2-x1)*0.2  # start cursors 20% from the midline 
    plotWidget.cursor2Pos = x1+(x2-x1)/2.+(x2-x1)*0.2 
    plotWidget.cursor1.setValue(plotWidget.cursor1Pos)
    plotWidget.cursor2.setValue(plotWidget.cursor2Pos)      
    plotWidget.addItem(plotWidget.cursor1)
    plotWidget.addItem(plotWidget.cursor2)

def hide_cursors(browser, plotWidget):
    """ Remove the data cursors.
    """
    #print(plotWidget.cursor1.value())
    plotWidget.cursor1Pos = []   
    plotWidget.cursor2Pos = []  
    plotWidget.removeItem(plotWidget.cursor1)
    plotWidget.removeItem(plotWidget.cursor2)
    plotWidget.cursor1.setValue('NaN')
    plotWidget.cursor2.setValue('NaN')

def replot_cursors(plotWidget):
    """ Replot the cursors in the current positions
    after the axis had been cleared for some reason
    """    
    plotWidget.addItem(plotWidget.cursor1)
    if hasattr(plotWidget, 'cursor2'):
        plotWidget.addItem(plotWidget.cursor2)     


def make_xvector(ydata, dt):
    """ Make a X vector to plot data against 
    and ensure it is has the same length as Y
    """ 
    x = np.arange(0, len(ydata)*dt, dt)
    if len(x)<len(ydata):
        x = np.append(x, dt)
    elif len(x)>len(ydata):
        x = np.delete(x, len(x)-1)
    return x 
