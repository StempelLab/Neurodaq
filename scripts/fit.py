
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from ...analysis import auxfuncs as aux
from ...util import pgplot
import pyqtgraph as pg
from analysis import smooth


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
        """ Parabolic function for variance-mean analysis with baseline variance
        """
        y = p[0] * x - (x**2)/p[1] + p[2]
        return y

    def ddm(self, x, *p):
        """ Drift difusion model reaction time 
        """
        y = p[0]/(p[1]*x) * np.tanh(p[0]*p[1]*x) + 0.2#+ p[2]
        return y

    def fit(self, fitFunc, x, y, p0):
        fitParams, fitCovariances = curve_fit(fitFunc, x, y, p0)  
        return fitParams

###################################################

# Get data
xRange = [25,40,75,98]
yData = [1.5, 1.3, 0.5, 0.3]
 
# Select function
dataFit = Fitting()
funcstring = 'ddm'
currentFuncmap = dataFit.fitfuncmap[funcstring]

# Set initial guesses
pInit = [] 
pInit.append(1)
pInit.append(0.1)
pInit.append(0)

# Fit data
func = currentFuncmap[0]
fitParams = dataFit.fit(func, xRange, yData, pInit) 
print(fitParams)
        
# Plot results
xRangeFit = np.arange(xRange[0], xRange[-1])
fittedTrace = func(xRangeFit, *fitParams)
plt.plot(xRangeFit, fittedTrace, 'r')
plt.plot(xRange, yData, 'k')

        



