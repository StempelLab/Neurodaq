""" Functions for plotting using matplotlib
"""

import sys, os, re, copy
import h5py
from PyQt5 import QtGui, QtCore, QtWidgets
import matplotlib.pyplot as plt

def plotSingleData(browser, plotWidget, data):
    plotWidget.canvas.ax.clear()
    plotWidget.canvas.ax.plot(data, 'k', linewidth=0.5)
    plotWidget.canvas.draw()


def plotMultipleData(browser, plotWidget):
    dt = 0.04
    plotWidget.canvas.ax.clear()
    plotWidget.plotDataIndex = []
    items = browser.ui.workingTree.selectedItems()
    if items:
        for item in items:
            if item.dataIndex is not None:
                x = np.arange(0, len(browser.ui.workingTree.data[item.dataIndex])*dt, dt)
                plotWidget.canvas.ax.plot(x, browser.ui.workingTree.data[item.dataIndex], 'k', linewidth=0.5)
                plotWidget.plotDataIndex.append(item.dataIndex)
            #if 'dataset' in str(browser.db[str(item.path)]):
            #    plotWidget.canvas.ax.plot(browser.db[str(item.path)][:], 'k')
    plotWidget.canvas.draw()            
    plotWidget.background = plotWidget.canvas.copy_from_bbox(plotWidget.canvas.ax.bbox)
    plotWidget.createCursor()
    if browser.ui.actionShowCursors.isChecked(): 
        plotWidget.showCursorLastPos()                 
    browser.ui.plotsWidget.homeAxis = browser.ui.plotsWidget.canvas.ax.axis()
