import numpy as np
import matplotlib.pylab as plt
import scipy.signal as signal
from analysis import smooth
from console import utils as ndaq

# data[0] has loom trigger events
# data[1] has X position data

# Get data
data = ndaq.get_data()

# Get trigger indices 
ivector = np.arange(0,len(data[0]))
itrigger = ivector[data[0]==1]

# Get loom events
pre = 200
post = 500
events = []
for i in itrigger:
    event = data[1][i-pre:i+post]
    events.append(event)
    #plt.plot(event)

#plt.show()
ndaq.store_data(events, name='loom_events')

# Detect failures and escape latency
nestPos = 400.0
escapeThs = -10.0  # derivative of X position
failures, latencies = [], []
devents = []
for event in events:
    if np.sum(event<nestPos)==0:
        failures.append(1)
    else:
        failures.append(0)
        devent = np.diff(event[pre::])
        latencies.append(np.sum(devent<escapeThs))
        devents.append(devent)

ndaq.store_data(devents, name='devents')
ndaq.store_data(failures, name='escape_failures')
ndaq.store_data(latencies, name='escape_latencies')


