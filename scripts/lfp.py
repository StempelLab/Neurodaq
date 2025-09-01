import numpy as np
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
from scripts import probeClass
from console import utils as ndaq

# Start probe object
#filedir = '/home/tiago/Data/Lab.local/PAG/probe/'
#filedir = '/home/tiago/Data/isilon-science/PAG_project/raw_data/behaviour/2015/15JUL05_Probe/2015-07-05_18-28-08/'
#filedir = '/home/tiago/Data/isilon-science/PAG_project/raw_data/behaviour/2015/15JUL2_Probe_SC/2015-07-02_19-48-34/'
filedir = '/home/tiago/Data/isilon-science/PAG_project/raw_data/behaviour/15JUL06_Probe_tests/2015-06-11_15-07-10 2/'
probe = probeClass.Probe(filedir)

# Choose channels
channels = np.arange(2,16)

# Load probe data and tdms
probe.load_nex(channels)
#probe.load_tdms()

# Get frame TTL for alignment
#probe.load_frameSignal()
#probe.get_frameIndex()

# Define analysis time window in datapoints
onset = 30000 #30000 #26900
pre = 200
post = 800
win = (onset-pre, onset+post)
win = (0,0)
#probe.get_dataWindow(win, tdms=True)
probe.get_probeDataWindow()

# Calculate time frequencies
f_start = 1.
f_stop = 150
deltafreq = (f_stop-f_start)/60.
#probe.get_timeFreq(probe.dataWin, f_start, f_stop, deltafreq)

# Make average spectogram
#tfrData = np.array([s.map for s in probe.tfrData])
#tfrMean = tfrData.mean(axis=0)

# Plot analysis
#for ax in canvas.fig.axes:
#    canvas.fig.delaxes(ax)
#nPlots = len(probe.tfrData)+2
#gs = gridspec.GridSpec(nPlots, 1)

#probe.tfrData[0].map = tfrMean # hack the tfr plotting method
#for plot in range(nPlots):
#    ax = canvas.fig.add_subplot(gs[plot])
#    if plot==0:
#        ax.plot(probe.spot)
#    elif plot==1:
#        ax.plot(probe.pos)
#    else:       
#        probe.tfrData[plot-2].plot(ax, colorbar=False, clim=[0,80])
#canvas.draw()


# Save to NDaq
#ndaq.store_data(probe.pos, name='position', attrs={'dt':20.})
#ndaq.store_data(probe.spot, name='visualStim', attrs={'dt':20.})
#ndaq.store_data(probe.dataWin, attrs={'dt': 1./30})
ndaq.store_data(probe.data, attrs={'dt': 1./30})


     

