""" Basic analysis functions for 1D data
"""

import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from widgets import h5Item
from ...util import pgplot
import smooth
import auxfuncs as aux


def baseline(browser):
    """ Subtract a baseline from the currently plotted traces.
    Baseline is the average of all datapoints between the 
    current position of the data cursors. 
    
    Options:
    1) keep original traces intact and create processed copies
    """
    plotWidget = browser.ui.dataPlotsWidget
    toolsWidget = browser.ui.toolStackedWidget   
    c1, c2 = aux.get_cursors(plotWidget) 

    # Check selected options
    for option in toolsWidget.baselineToolOptions:
        if option.isChecked():
            if option.text()=='Keep original data':
                aux.make_data_copy(browser, plotWidget)

    # Get the data now, in case we are working on a copy
    plotWidget.clear()    
    data = aux.get_data(browser)
    
    # Get dt list
    dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]

    # Make average between cursors and subract for each trace 
    for item in plotWidget.plotDataItems:
        bsl = np.mean(item.data[c1/dt:c2/dt])
        item.data = item.data - bsl

    # Re-plot data
    pgplot.replot(browser, plotWidget)
    pgplot.replot_cursors(browser, plotWidget)    

def average_traces(browser):
    """ Calculate average trace from currently plotted traces.

    Options:
    1) create new entry in Working Data tree with the result
    2) plot average with orginal traces
    """
    plotWidget = browser.ui.dataPlotsWidget
    toolsWidget = browser.ui.toolStackedWidget
    plotWidget.clear()
    data = aux.get_data(browser)   

    # Get dt list (at this stage they will all be the same 
    # because otherwise get_data would have thrown an error
    dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]
    
    # Calculate average
    avgData = np.mean(data,0)

    # Check selected options
    for option in toolsWidget.avgToolOptions:
        if option.isChecked():
            if option.text()=='Store result':
                results = []                
                # Get attributes from plotted items
                item = plotWidget.plotDataItems[0]
                attrs = item.attrs           
 
                # Store data     
                results.append(['avg_trace', avgData, attrs])
                aux.save_results(browser, item.parent().text(0)+'_average', results) 
            
            if option.text()=='Show traces':
                pgplot.replot(browser, plotWidget)
        
    # Plot average
    x = np.arange(0, len(avgData)*dt, dt)
    plotWidget.plot(x, avgData, pen=pg.mkPen('#CF1C04', width=2))
    if browser.ui.actionShowCursors.isChecked(): pgplot.replot_cursors(browser, plotWidget)      

def measure_cursor_stats(browser):
    """ Measure selected properties or statistics in the region defined
    by the data cursors.
    
    Options:
    1) create new entries in Working Data tree with the results
    """
    plotWidget = browser.ui.dataPlotsWidget
    toolsWidget = browser.ui.toolStackedWidget
    data = aux.get_data(browser)  
    c1, c2 = aux.get_cursors(plotWidget) 
    dataIndex = plotWidget.plotDataIndex     
    saveData = False

    # Get dt list
    dtList = aux.get_attr(plotWidget.plotDataItems, 'dt')

    # Go through data and check selected values to measure
    # Can probably do this in a more efficient way
    results = []
    for option in toolsWidget.measureToolOptions:
        if option.isChecked():
            if option.text()=='Store result':
                saveData = True        

            if option.text()=='Minimum':
                dataMin = []
                for t in range(len(data)):
                    dt = dtList[t]
                    y = np.min(data[t][c1/dt:c2/dt])
                    #x = np.where(data[t][c1:c2]==y)
                    x = np.argmin(data[t][c1/dt:c2/dt])
                    dataMin.append(y)
                    aux.plot_point(plotWidget, c1/dt, x, y, dt)
                results.append(['Minimum', dataMin])        

            if option.text()=='Maximum':
                dataMax = []
                for t in range(len(data)):
                    dt = dtList[t]
                    y = np.max(data[t][c1/dt:c2/dt])
                    #x = np.where(data[t][c1:c2]==y)
                    x = np.argmax(data[t][c1/dt:c2/dt])
                    dataMax.append(y)
                    aux.plot_point(plotWidget, c1/dt, x, y, dt)
                results.append(['Maximum', dataMax])    

            if option.text()=='Mean':
                dataMean = []
                for t in range(len(data)):
                    dt = dtList[t]
                    y = np.mean(data[t][c1/dt:c2/dt])
                    dataMean.append(y)
                    plotWidget.plot([c1,c2], [y,y], pen=pg.mkPen('#CF1C04', width=1))
                results.append(['Mean', dataMean])

    # Store results
    if saveData: aux.save_results(browser, 'Measurements', results)
    

def smooth_traces(browser):
    """ Smooth traces
    
    Options:
    1) Window type
    2) Window length
    """
    
    # Get options
    window = str(browser.ui.toolStackedWidget.smoothComboBox.currentText())
    window_len = float(browser.ui.toolStackedWidget.smoothLength.text())
    
    # Get data and widgets
    plotWidget = browser.ui.dataPlotsWidget
    toolsWidget = browser.ui.toolStackedWidget
    
    # Smooth data
    results = [] 
    for item in plotWidget.plotDataItems:  
        # Copy attributes and add some new ones
        attrs = item.attrs
        attrs['smooth_window_type'] = window
        attrs['smooth_window_length'] = window_len
        
        # Smooth
        traceSmooth = smooth.smooth(item.data, window_len=window_len, window=window)
        results.append([item.text(0), traceSmooth, attrs])
        
        # Plot smoothed trace
        x = np.arange(0, len(traceSmooth)*item.attrs['dt'], item.attrs['dt'])
        plotWidget.plot(x, traceSmooth, pen=pg.mkPen('#F2EF44', width=1))

    # Store results
    parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
    aux.save_results(browser, parentText+'_smooth', results)           
    
    
def custom_func(browser):
    """ Temporary function for user defined analysis.

    All options are harcoded and results are saved in a 
    "Analysis_results" folder in Root
 
    Additional items can be created by appending to the 
    'results' list in the forms ['name', data_to_be_stored, data_attributes]
    """

    # Get data and widgets
    plotWidget = browser.ui.dataPlotsWidget
    toolsWidget = browser.ui.toolStackedWidget
    
    # Get dt
    dt = aux.get_attr(plotWidget.plotDataItems, 'dt')[0]

    # Analyse data
    results = [] 
    for item in plotWidget.plotDataItems:          
        # Copy attributes and add some new ones
        attrs = item.attrs
        
        # USER DEFINED TRANSFORMATION
        USER_TRANSFORMED_DATA = item.data    

        # Append to storage list
        results.append(['NAME', USER_TRANSFORMED_DATA, attrs])
        
        # Plot modified trace if needed
        x = np.arange(0, len(USER_TRANSFORMED_DATA)*dt, dt)
        plotWidget.plot(x, USER_TRANSFORMED_DATA, pen=pg.mkPen('#F2EF44', width=1))

    # Store results
    aux.save_results(browser, 'Analysis_results', results)            

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    








