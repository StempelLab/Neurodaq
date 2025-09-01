""" Utility functions for IPython console
"""

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from widgets import h5Item
#from ..util import pgplot
from analysis import auxfuncs as aux


# Get browser instance
global browser

def set_browser(b):
    # Called by mainWindow.py to set global browser
    global browser
    browser = b


# Data functions
def get_data():
    """ Return the data currently plotted.
    """
    data = []
    for item in browser.ui.dataPlotsWidget.plotDataItems:
        dataRange, c1 = aux.get_dataRange(browser.ui.dataPlotsWidget, item)
        data.append(dataRange)
    data = np.array(data) # this will return an error if dts are different (data is not the same len)
    attrs = item.attrs    
    if data.shape[0]==1:
        return data.ravel()
    else:    
        return data
            
def get_items():
    items = []
    for item in browser.ui.dataPlotsWidget.plotDataItems:       
        items.append(item)
    return items

def store_data(data, array2D=False, name='data', attrs={'dt':1}):
    """ Adds data to the Data Tree

    'data' is a number array of 1 or 2 dimensions
    'name' is sring
    'attrs' is a dictionary {attr1: value1, attr2, value2, ...}
    
    If array2D==True the data are stored as a 2D-array
    """
    # Set root as parent
    parentWidget = browser.ui.workingDataTree.invisibleRootItem()

    # Make sure data is numpy array
    #data = np.array(data)

    # List - add 'name' group and 'data' datasets
    if isinstance(data, list):
        item = h5Item([name])
        browser.make_nameUnique(parentWidget, item, item.text(0)) 
        browser.ui.workingDataTree.addTopLevelItem(item)
        for n in np.arange(0, len(data)):
            child = h5Item(['data_'+str(n)])
            browser.make_nameUnique(item, child, child.text(0))
            child.data = data[n]
            child.attrs = attrs
            child.listIndex = len(browser.ui.workingDataTree.dataItems)
            browser.ui.workingDataTree.dataItems.append(child)
            item.addChild(child)

    # Float - add straight to root with name 'name' 
    #elif isinstance(data, float):
    #    item = h5Item([name])
    #    browser.make_nameUnique(parentWidget, item, item.text(0))    
    #    item.data = data
    #    item.attrs = attrs
    #    item.listIndex = len(browser.ui.workingDataTree.dataItems)
    #    browser.ui.workingDataTree.dataItems.append(item)
    #    browser.ui.workingDataTree.addTopLevelItem(item)

    # 1D array - add straight to root with name 'name' 
    elif (len(data.shape)==1) or ((len(data.shape)==2) and (array2D==True)):
        item = h5Item([name])
        browser.make_nameUnique(parentWidget, item, item.text(0))    
        item.data = data
        item.attrs = attrs
        item.listIndex = len(browser.ui.workingDataTree.dataItems)
        browser.ui.workingDataTree.dataItems.append(item)
        browser.ui.workingDataTree.addTopLevelItem(item)

    # 2D array - add 'name' group and 'data' datasets
    elif (len(data.shape)==2) and (array2D==False):
        item = h5Item([name])
        browser.make_nameUnique(parentWidget, item, item.text(0)) 
        browser.ui.workingDataTree.addTopLevelItem(item)
        for n in np.arange(0, len(data)):
            child = h5Item(['data_'+str(n)])
            browser.make_nameUnique(item, child, child.text(0))
            child.data = data[n,:]
            child.attrs = attrs
            child.listIndex = len(browser.ui.workingDataTree.dataItems)
            browser.ui.workingDataTree.dataItems.append(child)
            item.addChild(child)
            
            
# Ploting functions
def plot_data(*args, **kwargs): #color='#3790CC', clear=False):
    """ Plot a single trace.
    
    *args: y or x, y
    **kwargs: color='color', clear=True|False
    """
    plotWidget = browser.ui.dataPlotsWidget

    # Read option arguments
    options = {'color':'#3790CC', 'clear':False}
    options.update(kwargs)
    color = options['color']
    clear = options['clear']
    
    if clear: plotWidget.clear()
    if len(args)==1:
        plotWidget.plot(args[0], pen=pg.mkPen(color))
    elif len(args)==2:
        plotWidget.plot(args[0], args[1], pen=pg.mkPen(color))

def get_cursors(X=False):
    """ Returns the position of the 2 vertical cursors
    in the data plot tab. 

    c1, c2 = get_cursors()

    Default is to return in position in sampling points,
    set X=True to return positions in X-axis coordinates.
    """
    plotWidget = browser.ui.dataPlotsWidget
    c1 = plotWidget.cursor1.value()
    c2 = plotWidget.cursor2.value() 
    if c2<c1:        
        temp = c2
        c2 = c1
        c1 = temp
    dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]  # Assumes dt is the same for all plotted items
    if X:
        return int(c1), int(c2)
    else:
        return int(c1/dt), int(c2/dt)






 





