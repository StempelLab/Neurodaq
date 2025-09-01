import numpy as np
import matplotlib.pylab as plt
import scipy.signal as signal
from analysis import smooth
from console import utils as ndaq

# Display loom trials as a color coded raster

# Get data and items
data = ndaq.get_data()
items = ndaq.get_items()

# Put data into horizontal matrix
data = np.array(data)

# Show matrix
fig = plt.figure()
ax = fig.add_subplot(111)
ax.axis('off')
ax.matshow(data, cmap=plt.cm.hot)




