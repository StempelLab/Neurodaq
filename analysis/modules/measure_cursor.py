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
        self.entryName = 'Measure'
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
        # Set default values
        self.set_defaultValues()

    def make_option_widgets(self):
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Options')
        self.toolOptions = []

        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.storeBox = QtWidgets.QCheckBox('Store results')
        self.toolOptions.append([self.storeBox])
        #self.running = QtWidgets.QPushButton('Running')
        #self.running.setCheckable(True)
        self.minBox = QtWidgets.QCheckBox('Minimum')
        self.toolOptions.append([self.minBox])
        self.maxBox = QtWidgets.QCheckBox('Maximum')
        self.toolOptions.append([self.maxBox])
        self.areaBox = QtWidgets.QCheckBox('Area')
        self.toolOptions.append([self.areaBox])
        self.meanBox = QtWidgets.QCheckBox('Mean')
        self.toolOptions.append([self.meanBox])
        self.medianBox = QtWidgets.QCheckBox('Median')
        self.semBox = QtWidgets.QCheckBox('SEM')
        self.toolOptions.append([self.semBox])
        self.toolOptions.append([self.medianBox])
        self.peakComboBox = QtWidgets.QComboBox()
        self.peakComboBox.addItem('Positive peak')
        self.peakComboBox.addItem('Negative peak')
        self.toolOptions.append([self.peakComboBox])
        self.riseTimeBox = QtWidgets.QCheckBox('Rise time')
        self.toolOptions.append([self.riseTimeBox])
        self.riseLowerLimit = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Lower limit (%)'), self.riseLowerLimit])
        self.riseUpperLimit = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Upper limit (%)'), self.riseUpperLimit])
        self.onsetBox = QtWidgets.QCheckBox('Onset')
        self.toolOptions.append([self.onsetBox])
        self.decayTimeBox = QtWidgets.QCheckBox('Decay time')
        self.toolOptions.append([self.decayTimeBox])
        self.decayLimit = QtWidgets.QLineEdit()
        self.toolOptions.append([QtWidgets.QLabel('Decay limit (%)'), self.decayLimit])
        ############################################

        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def func(self, browser):
        """ Measure selected properties or statistics in the region defined
        by the data cursors.

        Rise time and onset are calculated by finding the peak and walking
        back until the limits are crossed. Onset limit is baseline mean; if
        no baseline has been set, it is taken as the mean value of the first
        1 ms of data.

        UPDATE: make onset limit X% of peak for events that are not aligned
        and therefore cannot be baselined properly

        Options:
        1) create new entries in Working Data tree with the results
        """

        ############################################
        # ANALYSIS FUNCTION

        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget

        # Replot data to clear previous measure plot points
        pgplot.replot(browser, plotWidget)

        # Iterate through traces
        dataMin, dataMax, dataArea, dataMean, dataMedian, dataSEM = [], [], [], [], [], []
        dataRiseTime, dataOnset, dataDecay = [], [], []
        dataMinX, dataMaxX = [], []
        for item in plotWidget.plotDataItems:

            # Get dt and data range
            dt = item.attrs['dt']
            data, c1, cx1, cx2 = aux.get_dataRange(plotWidget, item, cursors=True)

            # Check baseline
            if 'baselineStart' in item.analysis:
                bsl = 0  # the mean of the baseline will always be 0
            else:
                bsl = np.mean(data[0:round(1./dt)])

            # Measure selected parameters
            if self.minBox.isChecked():
                y = np.min(data)
                x = np.argmin(data)
                dataMin.append(y)
                dataMinX.append(x*dt)
                aux.plot_point(plotWidget, c1, x, y, dt)

            if self.maxBox.isChecked():
                y = np.max(data)
                x = np.argmax(data)
                dataMax.append(y)
                dataMaxX.append(x*dt)
                aux.plot_point(plotWidget, c1, x, y, dt)

            if self.areaBox.isChecked():
                y = np.trapz(data, dx=dt)
                dataArea.append(y)

            if self.meanBox.isChecked():
                y = np.mean(data)
                dataMean.append(y)
                plotWidget.plot([cx1,cx2], [y,y], pen=pg.mkPen('#CF1C04', width=1))

            if self.medianBox.isChecked():
                y = np.median(data)
                dataMedian.append(y)
                plotWidget.plot([cx1,cx2], [y,y], pen=pg.mkPen('#CF1C04', width=1))

            if self.semBox.isChecked():
                y = np.std(data)/np.sqrt(len(data))
                dataSEM.append(y)
                plotWidget.plot([cx1,cx2], [y,y], pen=pg.mkPen('#CF1C04', width=1))

            if self.riseTimeBox.isChecked():
                try:
                    lowerLimit = float(self.riseLowerLimit.text())/100
                    upperLimit = float(self.riseUpperLimit.text())/100
                except ValueError:
                    aux.error_box('Invalid limits')
                    return
                # Get peak
                xPeak, yPeak = self.get_peak(data)
                # Get limits
                lowerLimit = lowerLimit*(yPeak-bsl)+bsl
                upperLimit = upperLimit*(yPeak-bsl)+bsl
                # Find limit crosses
                lowerCrossed, upperCrossed = False, False
                i = 0
                while lowerCrossed==False or upperCrossed==False:
                    if (upperCrossed==False) and self.comp(data[xPeak-i],upperLimit):
                        xUpper = xPeak-i
                        upperCrossed = True
                    if self.comp(data[xPeak-i], lowerLimit):
                        xLower = xPeak-i
                        lowerCrossed = True
                    i+=1
                dataRiseTime.append((xUpper-xLower)*dt)
                # Plot points
                aux.plot_point(plotWidget, c1, xLower, lowerLimit, dt)
                aux.plot_point(plotWidget, c1, xUpper, upperLimit, dt)

            if self.onsetBox.isChecked():
                xPeak, yPeak = self.get_peak(data)
                bslCrossed = False
                i = 0
                limit = 0.1*yPeak # UPDATE
                while bslCrossed==False:
                    if self.comp(data[xPeak-i], limit):
                        onset = xPeak-i
                        bslCrossed = True
                    i+=1
                aux.plot_point(plotWidget, c1, onset, limit, dt)
                dataOnset.append(onset*dt)

            if self.decayTimeBox.isChecked():
                try:
                    decayLimit = float(self.decayLimit.text())/100
                except ValueError:
                    aux.error_box('Invalid limits')
                    return
                xPeak, yPeak = self.get_peak(data)
                yDecay = decayLimit*(yPeak-bsl)+bsl
                decayCrossed = False
                i = 0
                while decayCrossed==False:
                    if self.comp(data[xPeak+i], yDecay):
                        decayTime = xPeak+i
                        decayCrossed = True
                    i+=1
                aux.plot_point(plotWidget, c1, decayTime, yDecay, dt)
                dataDecay.append(decayTime*dt)

        # Store results
        results = []
        if self.storeBox.isChecked():
            if self.minBox.isChecked(): results.append(['Minimum', np.array(dataMin)])
            if self.minBox.isChecked(): results.append(['xMinimum', np.array(dataMinX)])
            if self.maxBox.isChecked(): results.append(['Maximum', np.array(dataMax)])
            if self.maxBox.isChecked(): results.append(['xMaximum', np.array(dataMaxX)])
            if self.areaBox.isChecked(): results.append(['Area', np.array(dataArea)])
            if self.meanBox.isChecked(): results.append(['Mean', np.array(dataMean)])
            if self.medianBox.isChecked(): results.append(['Median', np.array(dataMedian)])
            if self.semBox.isChecked(): results.append(['SEM', np.array(dataSEM)])
            if self.riseTimeBox.isChecked(): results.append(['RiseTime', np.array(dataRiseTime)])
            if self.onsetBox.isChecked(): results.append(['Onset', np.array(dataOnset)])
            if self.decayTimeBox.isChecked(): results.append(['Decay', np.array(dataDecay)])
            aux.save_results(browser, 'Measurements', results)
        ############################################

    def set_defaultValues(self):
        self.riseLowerLimit.setText('10')
        self.riseUpperLimit.setText('90')
        self.decayLimit.setText('37')

    def get_peak(self, data):
        peakDirection = str(self.peakComboBox.currentText())
        if peakDirection=='Positive peak':
            yPeak = np.max(data)
            xPeak = np.argmax(data)
        else:
            yPeak = np.min(data)
            xPeak = np.argmin(data)
        return xPeak, yPeak

    def comp(self, a, b):
        peakDirection = str(self.peakComboBox.currentText())
        if peakDirection=='Positive peak':
            return a < b
        else:
            return a > b
