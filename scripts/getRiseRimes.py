import numpy as np
import matplotlib.pylab as plt
import scipy.signal as signal
from analysis import smooth
from console import utils as ndaq

# Get data and items
data = ndaq.get_data()
items = ndaq.get_items()
dt = items[0].attrs['dt']

# Parameters
start = 0.2
end = 0.8

# Get peaks, decays and peak times
riseTimes = []
for trace in data:
    peak = trace.min()    
    peakTime = trace.argmin()
    riseTrace = trace[:peakTime]
    idx = (riseTrace<start*peak) & (riseTrace>end*peak)
    riseTime = np.sum(idx)*dt
    plt.plot(riseTrace[idx])
    print(peak*start, peak*end, riseTime)
    riseTimes.append(riseTime)
plt.show()

ndaq.store_data(riseTimes, name='rise_times')

