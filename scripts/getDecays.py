import numpy as np
import numpy as np
import matplotlib.pylab as plt
import scipy.signal as signal
from analysis import smooth
from console import utils as ndaq

# Get data and items
data = ndaq.get_data()
items = ndaq.get_items()
dt = items[0].attrs['dt']
dt = .04

# Get peaks, decays and peak times
decayTimes = []
for trace in data:
    peak = trace.min()
    decay = peak*0.37
    peakTime = trace.argmin()
    decayTrace = trace[peakTime:]
    idx = decayTrace<decay
    decayTime = np.sum(idx)*dt
    #plt.plot(decayTrace[idx])
    print(decayTime)
    decayTimes.append(decayTime)
#plt.show()

ndaq.store_data(decayTimes, name='decay_times')

