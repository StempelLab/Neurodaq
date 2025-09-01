# Get norm EPSP decay as a function of the time constant
#
# Select item with events to start
# Input time constant, select on EPSP with cursors where
# to measure. Takes the  x and y, and uses the x and the
# given tau to calculate what the decay of the membrane would
# be for that x
# Set 1 cursor for peak and one for decay

import numpy as np
import matplotlib.pylab as plt
import pyqtgraph as pg
from console import utils as ndaq

plotWidget = browser.ui.dataPlotsWidget

# Get data
items = ndaq.get_items()
c1, c2 = ndaq.get_cursors()
dt = items[0].attrs['dt']

# Setup exponential decay curve
xdecay = c2
xpeak = c1
tau = 43
x = np.arange(0, c2*dt-c1*dt, dt)

# Go through plotted traces
normDecays = []
for item in items:
    data = item.data
    ydecay = data[xdecay]
    ypeak = data[xpeak]
    if ydecay>ypeak: ydecay=ypeak*0.99  # for the cases it does not decay
    # Get values from theoretical curve
    y = ypeak * np.exp(-(x/tau))  # don't need this, just for plotting
    tDecay = -tau * np.log(ydecay/ypeak)
    # Normalise
    #print(ydecay, (xdecay-xpeak)*dt, tDecay)
    val = (xdecay-xpeak)*dt/tDecay
    if not np.isnan(val): normDecays.append(val)

# Plot decay curve
plotWidget.plot(x+c1*dt, y, pen=pg.mkPen('r', width=1))

# Save data
ndaq.store_data(np.array(normDecays), name='decays')
print(np.mean(normDecays), normDecays)
