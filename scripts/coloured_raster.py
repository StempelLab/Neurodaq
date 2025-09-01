import numpy as np
import matplotlib.pylab as plt
from analysis import smooth
from console import utils as ndaq
import matplotlib as mpl
import matplotlib.gridspec as gridspec

# Display loom trials as a color coded raster,
# Updates by Dom: normalise to max, color bar, aspect=auto

# Get data
data = ndaq.get_data()

# Put data into horizontal matrix
data = np.array(data)

# Rank by latency to peak
#maxIndex = np.argmax(data, axis=1)
#index = np.argsort(maxIndex)
#rankedData = [data[i] for i in index]
#rankedData = np.array(rankedData)
#rankedData = data

# Define max value for normalization
vmax = 30
vmin = -0

# Colormap
#cmap = plt.cm.Spectral_r
cmap = plt.cm.hot

# Remove all existing axes
for ax in canvas.fig.axes:
    canvas.fig.delaxes(ax)

# Create grid
nPlots, width_ratios = 2, [10,1]
gs = gridspec.GridSpec(1, nPlots, width_ratios=width_ratios)

# Create subplots
ax = []
for plot in range(nPlots):
    ax.append(canvas.fig.add_subplot(gs[plot]))

# Show matrix
#ax[0].axis('off')
#ax.linewidth=50.0
ax[0].matshow(rankedData, cmap=cmap, vmin=vmin, vmax=vmax, interpolation='none',aspect='auto')
norm = mpl.colors.Normalize(vmin=0, vmax=vmax)

# Show colorbar
cbar = mpl.colorbar.ColorbarBase(ax[1], cmap=cmap, norm=norm, spacing='proportional')
cbar.set_label('cm/s', rotation=0, labelpad=10, y=1)
cbar.set_ticklabels(['Low', 'Medium'])# horizontal colorbar
mpl.rcParams.update({'font.size': 14})

canvas.draw()
