# Get onsets after manually sorting cut events
# 
# Select item with events to start

import numpy as np
import matplotlib.pylab as plt
from console import utils as ndaq

# Get data
item =  browser.ui.workingDataTree.selectedItems()[0]

# Iterate events and get onsets
onsets = []
for c in range(item.childCount()):
    onsets.append(item.child(c).attrs['onset'])

# Save
ndaq.store_data(np.array(onsets), name='xOnsets')

