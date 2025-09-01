# Make instantaneous frequency histograms from
# xOnset data after event detection
# 
# Select item "cell_N" containing items "trace" and "xOnset"

import numpy as np
import matplotlib.pylab as plt
from analysis import smooth
from console import utils as ndaq

# Get data
item =  browser.ui.workingDataTree.selectedItems()[0]
print(item.text(0))
for c in range(item.childCount()):
    if 'trace' in item.child(c).text(0): trace = item.child(c)
    if 'xOnsets' in item.child(c).text(0): xonsets = item.child(c).data

# xOnsets is in datapoints, convert to ms
dt = trace.attrs['dt']
xonsets = xonsets * dt

# Convert to frequency
freq = 1000./np.diff(xonsets)

# Make histogram
nbins = 100
binsRange = (0,20)
n, bins, patches = plt.hist(freq, bins=nbins, range=binsRange, normed=False, histtype='stepfilled')
n = n/float(np.sum(n))

# Store data
ndaq.store_data(n, name='n')
ndaq.store_data(bins, name='bins')
ndaq.store_data(np.array(freq), name='median_freq') 



# AP nbins = 50, binsRange = 10
# EPSC nbins = 0, binsRange = 10
