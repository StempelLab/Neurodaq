""" Event detection functions
"""

import numpy as np
import scipy.signal as signal
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from widgets import h5Item
from ...util import pgplot
import auxfuncs as aux
import smooth

# TO DO:
# manually add and remove events from plot by clicking
# replot events detected after loading


def event_detect(browser):
    """ Temporary event detection function using amplitude
    threshold only. Noise safety is for when coming down from
    peak, go down an extra amount from threshold before starting
    to search for the next event.
    """
    # Read detection options 
    threshold = float(browser.ui.dataPlotsWidget.cursorThsPos)
    noiseSafety = float(browser.ui.toolStackedWidget.eventNoiseSafety.text())
    smoothFactor = float(browser.ui.toolStackedWidget.eventSmooth.text())
    direction = str(browser.ui.toolStackedWidget.eventDirection.currentText())
    c1, c2 = aux.get_cursors(browser.ui.dataPlotsWidget) 

    # Ensure that noise safety has the same sign as the threshold
    noiseSafety = np.sign(threshold) * abs(noiseSafety)

    # Get dt list and attrs for use in concatenated data
    dtList = aux.get_attr(browser.ui.dataPlotsWidget.plotDataItems, 'dt')
    dt = dtList[0]
    item = browser.ui.dataPlotsWidget.plotDataItems[0]
    attrs = item.attrs

    # Get data currently plotted within the cursors and concatenate in a single sweep
    data = aux.get_data(browser)
    if browser.ui.dataPlotsWidget.cursor1Pos: data = data[:,c1/dt:c2/dt]
    data = data.ravel()

    # Smooth
    original_data = data
    if smoothFactor > 1:
        data = smooth.smooth(data, window_len=smoothFactor, window='hanning')

    # Run detection  
    if direction=='negative':
        comp = lambda a, b: a < b
    elif direction=='positive':
        comp = lambda a, b: a > b
    eventCounter,i = 0,0
    xOnsets, yOnsets = [], []
    while i<len(data):
        if comp(data[i],threshold):
            xOnsets.append(i)
            yOnsets.append(data[i])
            eventCounter +=1
            while i<len(data) and comp(data[i],(threshold-noiseSafety)):
                i+=1 # skip values if index in bounds AND until the value is below/above threshold again
        else:
            i+=1

    frequency = eventCounter/(len(data)*dt)*1000   # in Hz
    print(eventCounter, 'events detected at', frequency, 'Hz')

    # Store event onsets and peaks in h5 data tree
    results = []
    results.append(['trace', np.array(original_data), attrs])
    results.append(['onsets', np.array(xOnsets)])
    results.append(['peaks', np.array(yOnsets)])
    results.append(['number', np.array([eventCounter])])
    results.append(['frequency', np.array([frequency])])
    listIndexes = aux.save_results(browser, 'Event_Detection', results)    

    # Store list indexes temporarily in stack widget list for further event analysis
    browser.ui.toolStackedWidget.eventItemsIndex = listIndexes

#    browser.ui.toolStackedWidget.eventData.append(np.array(original_data))
#    browser.ui.toolStackedWidget.eventData.append(np.array(data))
#    browser.ui.toolStackedWidget.eventData.append(np.array(xOnsets))
#    browser.ui.toolStackedWidget.eventData.append(dt)

    # Plot results
    show_events(browser, data, np.array(xOnsets), np.array(yOnsets), dt)

def event_cut(browser):
    # Get trace and event onsets using stored dataIndex
    itrace = browser.ui.toolStackedWidget.eventItemsIndex[0]
    trace = browser.ui.workingDataTree.dataItems[itrace]
    ionsets = browser.ui.toolStackedWidget.eventItemsIndex[1]
    onsets = browser.ui.workingDataTree.dataItems[ionsets]   
    dt = float(trace.attrs['dt'])

    # Get cutting parameters
    baseline = float(browser.ui.toolStackedWidget.eventBaseline.text())/dt
    duration = float(browser.ui.toolStackedWidget.eventDuration.text())/dt 

    # Cut out
    events = []
    for onset in onsets.data:
        eStart = onset-baseline
        eEnd = onset+duration
        eData = trace.data[eStart:eEnd]
        events.append(eData)

    # Store event waveforms in h5 data tree
    results = []
    attrs = {}
    attrs['dt'] = dt 
    for e in np.arange(0, len(events)):
        results.append(['event'+str(e), events[e], attrs])  
    aux.save_results(browser, 'Events', results)


def show_events(browser, data, xOnsets, yOnsets, dt):
    plotWidget = browser.ui.dataPlotsWidget
    plotWidget.clear()
    x = np.arange(0, len(data)*dt, dt)
    plotWidget.plot(x, data)
    plotWidget.plot(xOnsets*dt, yOnsets, pen=None, symbol='o', symbolPen='r', symbolBrush=None, symbolSize=7)



