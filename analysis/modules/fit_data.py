from PyQt5 import QtGui, QtCore, QtWidgets

####################################
# ADD ADDITIONAL IMPORT MODULES HERE
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from analysis import auxfuncs as aux
from util import pgplot
import pyqtgraph as pg
from analysis import smooth
####################################

class AnalysisModule():    

    def __init__(self, browser):    
    
        ############################################
        # NAME THAT IS LISTED IN THE TAB
        self.entryName = 'Fit'  
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
        # Initialise Fitting Class
        self.dataFit = Fitting()
        # Initialize widgets and labels to first function on the list
        self.update_tab(0)

    
    def make_option_widgets(self):         
        stackWidget = self.browser.ui.oneDimToolStackedWidget
        self.toolGroupBox = QtWidgets.QGroupBox('Function')
        self.toolOptions = []
        
        ############################################
        # WIDGETS FOR USER DEFINED OPTIONS
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItem('line')
        self.comboBox.addItem('exp')
        self.comboBox.addItem('expsum')
        self.comboBox.addItem('parab')
        self.comboBox.addItem('ddm')
        self.comboBox.addItem('logistic')
        self.comboBox.addItem('logistic_offset')
        self.toolOptions.append([self.comboBox])
        self.storeBox = QtWidgets.QCheckBox('Store results')
        self.toolOptions.append([self.storeBox])        
        self.extendBox = QtWidgets.QCheckBox('Extend to data range')
        self.toolOptions.append([self.extendBox])       
        self.toolOptions.append([QtWidgets.QLabel('Initial guesses')])
        self.p, self.plabels = [], []
        self.make_parameterWidgets(10) # arbitrary number of max parameters   

        self.comboBox.currentIndexChanged.connect(self.update_tab)   
        ############################################        
              
        stackWidget.add_options(self.toolOptions, self.toolGroupBox, self.entryName)

    def make_parameterWidgets(self, n):
        for w in np.arange(0,n):
            self.p.append(QtWidgets.QLineEdit())
            self.plabels.append(QtWidgets.QLabel('test'))
            self.toolOptions.append([self.plabels[w], self.p[w]])

    def update_tab(self, text):
        """ Update labels and options in tab according to selected function.
        """
        selection = str(self.comboBox.currentText())
        for func in self.dataFit.fitfuncmap:
            if func==selection:
                self.comboBox.setToolTip(self.dataFit.fitfuncmap[func][3][0])
                nParam = len(self.dataFit.fitfuncmap[func][2])
                for n in range(nParam):
                    self.p[n].show()
                    self.plabels[n].show()
                    self.p[n].setText(str(self.dataFit.fitfuncmap[func][1][n]))
                    self.plabels[n].setText(self.dataFit.fitfuncmap[func][2][n]) 
                for n in np.arange(len(self.p)-(len(self.p)-nParam), len(self.p)):
                    self.p[n].hide()
                    self.plabels[n].hide()

    def func(self, browser):
        """ Fit data traces within cursor-defined range
    
        Options:
        1) Equation
        2) Initial guesses
        """
    
        ############################################
        # ANALYSIS FUNCTION
        
        # Get widgets
        plotWidget = browser.ui.dataPlotsWidget
        toolsWidget = browser.ui.oneDimToolStackedWidget

        # Replot data to clear previous measure plot points
        pgplot.replot(browser, plotWidget)
    
        # Get parent text of plotted items
        try:
            parentText = plotWidget.plotDataItems[0].parent().text(0) # Assumes all plotted data have the same parent
        except AttributeError:   # Parent = None
            parentText = 'Data'

        # Get current function
        currentFuncmap = self.dataFit.fitfuncmap[str(self.comboBox.currentText())]

        # Read initial guesses
        pInit = []
        try:        
            nParam = len(currentFuncmap[2])
            for n in range(nParam): pInit.append(float(self.p[n].text()))
        except ValueError:
            aux.error_box('Invalid value in initial guess')
            return              

        # Fit data
        fitResults, fitTraces, fitTracesAttrs = [], [], []
        print(pInit)
        for item in plotWidget.plotDataItems:  

            # Get data range to fit        
            dt = item.attrs['dt']
            fitTracesAttrs.append(item.attrs)
            yData, c1, cx1, cx2 = aux.get_dataRange(plotWidget, item, cursors=True)
            xRange = pgplot.make_xvector(yData, dt)+cx1
            self.dataFit.c1 = cx1   

            # Fit
            func = currentFuncmap[0]
            fitParams = self.dataFit.fit(func, xRange, yData, pInit) 
            fitResults.append(fitParams)
            print(fitParams)
        
            # Plot fitted function over trace
            if self.extendBox.isChecked():
                xRange = pgplot.make_xvector(item.data, dt)
                #xRange = np.arange(plotWidget.viewBox.viewRange()[0][0], plotWidget.viewBox.viewRange()[0][1], dt)
            fittedTrace = func(xRange, *fitParams)
            plotWidget.plot(xRange, fittedTrace, pen=pg.mkPen('r', width=1))
            fitTraces.append(fittedTrace)

        # Store results
        if self.storeBox.isChecked():
            fitResults = np.array(fitResults)
            results = []
            for n in range(np.shape(fitResults)[1]):    
                results.append([str(self.plabels[n].text()), fitResults[:,n]])
            for n in range(len(fitTraces)):
                results.append(['fitTraces_'+str(n), fitTraces[n], fitTracesAttrs[n]])     
            aux.save_results(browser, parentText+'_fit', results)     
         
        ############################################  

class Fitting:
    """ Class for fitting data.
    Dictionary with functions contains: function call, initial parameters, names
    of parameters, equation

    Based on Fitting.py from acq4 by Paul Manis 
    (https://github.com/acq4/acq4/blob/develop/acq4/analysis/tools/Fitting.py)
    """

    def __init__(self):
        self.c1 = 0
        self.c2 = 0
        self.fitfuncmap = {
        'line' : (self.line, [1.0, 0.0], ['m', 'b'], ['m*x + b']),
        'exp'  : (self.exp, [0.0, 1.0, 20.0], ['Y0', 'A', 'tau'],
                  ['Y0 + A*exp(-(x-X0)/tau)']),
        'expsum'  : (self.expsum, [0.0, 1.0, 20.0, 1.0, 20.0], ['Y0', 'A1', 'tau1', 'A2', 'tau2'],
                  ['Y0 + A1*exp(-(x-X0)/tau1) + A2*exp(-(x-X0)/tau2)']),
        'parab' : (self.parab, [-10.0, 10.0, 0.0], ['i', 'N', 'bsl'],
                  ['i * x-x^2/N + bsl']),
        'ddm' : (self.ddm, [1.0, 0.1, 0.0], ['A', 'k', 't'], ['A/(k*x) * np.tanh(A*k*x)']),
        'logistic' : (self.logistic, [1.0, 1.0, 0.0], ['L', 'k', 'x0'],
                    ['L/(1 + np.exp(-k * (x-x0)))']),
        'logistic_offset' : (self.logistic_offset, [0.0, 1.0, 1.0, 0.0], ['vmax', 'vmin', 'k', 'x0'],
                    ['vmin+(vmax-vmix)/(1 + np.exp(-k * (x-x0)))']) 
        }

    def line(self, x, *p):
        """ Line function
        """
        y = p[0]*x + p[1]
        return y

    def exp(self, x, *p):
        """ Exponential function with amplitude and X and Y offset
        """
        y = p[0] + p[1] * np.exp(-(x-self.c1)/p[2])
        return y

    def expsum(self, x, *p):
        """ Sum of two exponentials with independent time constants and amplitudes,
        and X and Y offsets
        """
        y = p[0] + p[1]*np.exp(-(x-self.c1)/p[2]) + p[3]*np.exp(-(x-self.c1)/p[4])    
        return y

    def parab(self, x, p):
        """ Parabolic function for variance-mean analysis with basline variance
        """
        y = p[0] * x - (x**2)/p[1] + p[2]
        return y

    def ddm(self, x, *p):
        """ Drift difusion model reaction time 
        """
        y = p[0]/(p[1]*x) * np.tanh(p[0]*p[1]*x) + p[2]
        return y

    def logistic(self, x, *p):
        """ Logistic function
        """
        y = p[0]/(1 + np.exp(-p[1] * (x-p[2])))
        return y

    def logistic_offset(self, x, *p):
        """ Logistic function with a y offset
        """
        y = p[0]+(p[1]-p[0])/(1 + np.exp(-p[2] * (x-p[3])))
        return y

    def fit(self, fitFunc, x, y, p0):
        fitParams, fitCovariances = curve_fit(fitFunc, x, y, p0)  
        return fitParams




