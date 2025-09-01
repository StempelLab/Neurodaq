# Get AP thresholds using a derivative threshold

import numpy as np
import matplotlib.pylab as plt
from analysis import smooth
from console import utils as ndaq

# Get data
data = ndaq.get_data()
dt = browser.ui.dataPlotsWidget.plotDataItems[0].attrs['dt']

# Get thresholds
cutoff = 10.0  # mV/mv
ths = []
for d in data:
    diff = np.diff(d)/dt
    i = diff>cutoff
    l = np.arange(len(i))
    ths.append(d[l[0]])

# Store data
m = np.mean(ths)
print(m)
ndaq.store_data(np.array(ths), name='AP_ths')
