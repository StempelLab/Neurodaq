import numpy as np
import matplotlib.pylab as plt
import scipy.signal as signal
from analysis import smooth
from console import utils as ndaq

# Get data and items
data = ndaq.get_data()
items = ndaq.get_items()
dt = items[0].attrs['dt']

# Make average trace
avg = data.mean(0)
avgPeak = avg.min()
xpeak = np.argmin(avg)

# Clear plot
#ndaq.plot_data([0], clear=True)

# Go through events
results1, results2 = [], []
nbins = 30
for trace in data:
    # Scale average
    peak = trace.min()
    sf = peak/avgPeak
    scaledAvg = avg*sf

    # Get decay part only
    decay = trace[xpeak+25:]
    avgDecay = scaledAvg[xpeak+25:]
    plt.plot(scaledAvg, 'r')
    plt.plot(trace, 'k')
    plt.plot((decay-avgDecay)**2)

    # Divide into bins
    binSize = decay.min()/nbins    

    # Get mean and variance current per bin
    m, v = [], []
    for b in range(nbins):
        ymin = b*binSize
        ymax = (b+1)*binSize
        i = (decay<ymin) & (decay>ymax)  # For inward currents
        current = decay[i].mean()
        var = (np.sum((decay[i]-avgDecay[i])**2))/(np.sum(i)-1)
        
        m.append(current)
        v.append(var)
    
    results1.append(np.array(m))
    results2.append(np.array(v)) 
    ndaq.plot_data(np.array(m), np.array(v))

plt.show()
# Store
ndaq.store_data(results1)
ndaq.store_data(results2)

