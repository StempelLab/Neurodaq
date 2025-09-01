# various plots

import numpy as np
import matplotlib.pylab as plt
from analysis import smooth
from console import utils as ndaq
import matplotlib as mpl
import matplotlib.gridspec as gridspec

# Plot mean and error as shade
# Data as [avg+sem, avg-sem, avg]

# Get data
data = ndaq.get_data()

# Put data into horizontal matrix
data = np.array(data)

# Remove all existing axes
for ax in canvas.fig.axes:
    canvas.fig.delaxes(ax)

# Create grid
nPlots, width_ratios = 1, [1]
gs = gridspec.GridSpec(1, nPlots, width_ratios=width_ratios)

# Create subplots
ax = []
for plot in range(nPlots):
    ax.append(canvas.fig.add_subplot(gs[plot]))

# Plot

# Filled histogram and error
#x = np.arange(0.1,10.1,0.1)
#ax[0].fill(x, data[0], 'k')
#ax[0].fill(x, data[1], 'y')
#ax[0].fill(x, data[2], 'g')

# Line plots
#x = np.arange(0,len(data)*0.02,0.02)
x = np.arange(0, len(data[0]))

#x = data[0]
ax[0].plot(x, data[0], 'k')
ax[0].plot(x, data[1], 'y')
ax[0].plot(x, data[2], 'g')
ax[0].set_ylim([100,220])

# Histogram from plotted data
#ax[0].hist(data, bins=20, range=(0,10), histtype='stepfilled')
#ax[0].hist(data[1], bins=40, range=(-200,10), histtype='bar')
#ax[0].hist(data[2], bins=40, range=(-200,10), histtype='bar')

#ax[0].plot(x, data[0], 'k')
#ax[0].plot(x, data[1], 'y')
#ax[0].plot(x, data[2], 'g')
#ax[0].set_xlim([0,20])


# Symbols
#x = np.zeros(len(data))
#ax[0].plot(x, data, 'o')
#ax[0].set_ylim([0,200])

# Bar chart
#x = np.arange(0, len(data[0]))
#ax[0].bar(x, data[0], 1.0, color='r', yerr=data[1])
#ax[0].bar(x, data[1], 17.5, color='y')
#ax[0].bar(x, data[2], 1.0, color='g')
#ax[0].set_ylim([0,110])

#x = np.arange(0, len(data[0]))
#ax[0].bar(x, data[0], 1.0, color='r', yerr=data[1])
#ax[0].bar(x, data[1], 17.5, color='y')
#ax[0].bar(x, data[2], 1.0, color='g')
#ax[0].set_ylim([0,110])


# Raster
#colors = ['#DF0101', '#08298A', '#0080FF', '#01DFD7', '#01DF74', '#01DF74', '#01DF74', '#01DF74', '#01DF74', '#8A084B']
#for n in range(len(data)):
    #x = np.ones(len(data[n]))*n
    #ax[0].plot(x, data[n], '_')
#    plotdata = np.flipud(data[n])
#    for p in range(len(data[n])):
#        if p==0:
#            c = colors[0]
#        else:
#            c = colors[2]
#        ax[0].plot(n, plotdata[p], '.', color=c)

canvas.draw()
