# Class for fitting functions to data using scipy.optimize
# Use by instantianting the class and calling:
# fitParams = self.dataFit.fit(func, x, y, pInit)
# "func" is a dictionary entry in fitfuncmap

import numpy as np
from scipy.optimize import curve_fit


class Fitting:
    """ Class for fitting data.
    Dictionary with functions contains: function call, initial parameters, names
    of parameters, equation

    c1 is used to define an X offset if needed

    Based on Fitting.py from acq4 by Paul Manis
    (https://github.com/acq4/acq4/blob/develop/acq4/analysis/tools/Fitting.py)
    """

    def __init__(self):
        self.c1 = 0
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

    def parab(self, x, *p):
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
        """ Fit fitFunc to x and y data
        """
        fitParams, fitCovariances = curve_fit(fitFunc, x, y, p0)
        return fitParams

    def getFitTrace(self, fitFunc, x, fitParams, dx=None):
        """ Generate y data with the fitted parameters
        Option to specify dx, to have dx different than the original x vector
        """
        if dx is not None:
            x = np.arange(x[0], x[-1], dx)
        return fitFunc(x, *fitParams)
