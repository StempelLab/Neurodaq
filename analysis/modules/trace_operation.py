from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
####################################

class AnalysisModule():

    def __init__(self, browser):

        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Trace operations'
        ############################################

        # Get main browser
        self.browser = browser
        # Add entry to AnalysisSelectWidget
        selectItem = QtGui.QStandardItem(self.entryName)
        selectWidget = self.browser.ui.oneDimToolSelect
        selectWidget.model.appendRow(selectItem)
        # Add entry to tool selector
        browser.customToolSelector.add_tool(self.entryName, self.func)
        # Add option widgets
        self.make_option_widgets()

        selectItem.setToolTip('Perform operations in plotted traces')

    def make_option_widgets(self):
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []

        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.keepData = QtWidgets.QCheckBox('Keep original data')
        self.toolOptions.append([self.keepData])
        self.delPointsBox = QtWidgets.QCheckBox('Delete points')
        self.toolOptions.append([self.delPointsBox])
        self.offsetBox = QtWidgets.QCheckBox('Offset points')
        self.offsetPoints = QtWidgets.QLineEdit()
        self.toolOptions.append([self.offsetBox, self.offsetPoints])
        self.cursorOffsetBox = QtWidgets.QCheckBox('Cursor Offset')
        self.toolOptions.append([self.cursorOffsetBox])
        self.scaleBox = QtWidgets.QCheckBox('Scale')
        self.scaleValue = QtWidgets.QLineEdit()
        self.toolOptions.append([self.scaleBox, self.scaleValue])
        self.normalizeBox = QtWidgets.QCheckBox('Normalize peak')
        self.peakComboBox = QtWidgets.QComboBox()
        self.peakComboBox.addItem('Positive')
        self.peakComboBox.addItem('Negative')
        self.toolOptions.append([self.normalizeBox, self.peakComboBox])
        self.normalizeAvgBox = QtWidgets.QCheckBox('Normalize mean')
        self.toolOptions.append([self.normalizeAvgBox])
        self.selectedBox = QtWidgets.QCheckBox('Data operation')
        self.selectedComboBox = QtWidgets.QComboBox()
        self.selectedComboBox.addItem('Subtract')
        self.selectedComboBox.addItem('Add')
        self.toolOptions.append([self.selectedBox, self.selectedComboBox])

        ############################################

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Perform some operations on selected traces.

        Options:
        1) keep original traces intact and create processed copies
        2) delete the data points between the cursors
        3) offset the start of the trace by a number of X-axis points (adds NaNs)
        """

        ############################################
        # ANALYSIS FUNCTION

        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget

        # Get options
        if self.offsetBox.isChecked():
          try:
            nOffsetPoints = float(self.offsetPoints.text())
          except ValueError:
            aux.error_box('Invalid number of points')
            return

        if self.scaleBox.isChecked():
          try:
            vScale = float(self.scaleValue.text())
          except ValueError:
            aux.error_box('Invalid scale entry')
            return

        # Copy data if required
        if self.keepData.isChecked():
            aux.make_data_copy(browser, plotWidget)

        # Iterate through traces
        i = 0
        for item in plotWidget.plotDataItems:

            # Get dt and data range
            dt = item.attrs['dt']
            data, c1, cx1, cx2 = aux.get_dataRange(plotWidget, item, cursors=True)

            # Check baseline
            if 'baselineStart' in item.analysis:
                bsl = 0  # the mean of the baseline will always be 0
            else:
                bsl = np.mean(item.data[0:round(1./dt)])

            # Scale data
            if self.scaleBox.isChecked():
                item.data = item.data * vScale

            if self.normalizeBox.isChecked():
                peakDirection = str(self.peakComboBox.currentText())
                if peakDirection=='Positive':
                    peak = np.max(data)
                else:
                    peak = -np.min(data)
                item.data = item.data / peak

            if self.normalizeAvgBox.isChecked():
                item.data = item.data/data.mean()

            # Delete points
            if self.delPointsBox.isChecked():
                item.data = np.delete(item.data, np.s_[c1:c1+len(data)+1])

            # Add offset
            if self.offsetBox.isChecked():
                offset = int(nOffsetPoints/dt)
                item.data = np.insert(item.data, 0, np.zeros(offset) + np.nan)

            # Cursor offset (add c2-c1 NaNs to the start)
            if self.cursorOffsetBox.isChecked():
                offset = int((cx2-cx1)/dt)
                item.data = np.hstack((np.zeros(offset) + np.nan, item.data))

            # Operation against selected data (currently only works for one selected data item)
            if self.selectedBox.isChecked():
                operation = str(self.selectedComboBox.currentText())
                if operation=='Subtract':
                    op = lambda a, b: a - b
                if operation=='Add':
                    op = lambda a, b: a + b
                try:
                    selectedItem = browser.ui.workingDataTree.selectedItems()[i]
                    item.data = op(item.data, selectedItem.data)
                except IndexError:
                    aux.error_box('Number of selected data items does not match number of plotted traces')
                    return
            i+=1

        # Re-plot data
        pgplot.replot(browser, plotWidget)

        ############################################
