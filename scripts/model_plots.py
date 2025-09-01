import numpy as np
import matplotlib.pylab as plt
from analysis import smooth
from console import utils as ndaq
import matplotlib as mpl
import matplotlib.gridspec as gridspec

# Display simulation data iterating 2 variables
# currently for showing the average derivative of EPSPs over
# the first 'dur' ms

# Values
shape = (41,41)
stOnset = 705
dur = 50
dt = 0.05
nstart = int(stOnset/dt)
nend = nstart + int(dur/dt)

# Get data
item =  browser.ui.workingDataTree.selectedItems()[0]

# Iterate events, get data and derivative
data = []
for c in range(item.childCount()):
    v = item.child(c).data
    #diff = np.diff(v)
    #if v[nstart:nend].max()>-29:
        #d = 0.032 
    #    d = diff[nstart:nend].mean()        
    #else:
    #    d = diff[nstart:nend].mean()
    b = v[int(700/0.05)]
    ypeak = v[int(704/0.05)]-b
    ydecay = v[int(854/0.05)]-b 
    tDecay = -10 * np.log(ydecay/ypeak) 
    d = 150/tDecay
    #d = np.log2(d)    
    if ydecay>ypeak: d=100 
    data.append(d) 
data = np.array(data)
#data = ndaq.get_data()

# Put data into  matrix
data.shape = shape

# Define max value for normalization
vmax = 5 #data.max()
vmin = 1 #data.min()

# Colormap
#cmap = plt.cm.bwr
#cmap = plt.cm.BrBG
cmap = plt.cm.gist_heat
cmap.set_over(color='#7F4E52')

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
ax[0].matshow(data, cmap=cmap, vmin=vmin, vmax=vmax, interpolation='none',aspect='auto')
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)    

# Show colorbar
cbar = mpl.colorbar.ColorbarBase(ax[1], cmap=cmap, norm=norm, spacing='proportional')
#cbar.set_label('cm/s', rotation=0, labelpad=10, y=1)
cbar.set_ticklabels(['Low', 'Medium'])# horizontal colorbar
mpl.rcParams.update({'font.size': 14})

canvas.draw()


# get some values
gRange = np.arange(0.71,0.75,0.001)
a = []
for g1 in gRange:
    for g2 in gRange:
        a.append((g1, g2))
#print(a[986])
