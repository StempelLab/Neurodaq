import numpy as np
import matplotlib.pylab as plt
from console import utils as ndaq

data = []
items = browser.ui.workingDataTree.selectedItems()
for item in items:
    for i in np.arange(item.childCount()):
        if 'ROI' in item.child(i).text(0):
            data.append(item.child(i).data)
