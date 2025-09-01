# Get number of events between resting Vm and AP
# and the time between the last event and the AP
#
# Data is AP sweeps with 500 ms before

import numpy as np
import matplotlib.pylab as plt
import pyqtgraph as pg
from ..acq4 import filterfuncs as acq4filter
from console import utils as ndaq

plotWidget = browser.ui.dataPlotsWidget

# Parameters
AP_time = 500
AP_winCut = 30  # window before AP to start looking, otherwise the AP rise gets detected
threshold = 0.004
noiseSafety = 0.0015
vm = -48
vmWin = 1

# Functions
comp = lambda a, b: a > b
def detect(data):
    dtrace = np.diff(data)
    dtrace = acq4filter.besselFilter(dtrace, 2000, 1, dt/1000, 'low', True)
    eventCounter,i = 0,0 
    xOnsets, vmPoints = [], []
    bsl = 0
    detectionData = dtrace
    while i<len(detectionData):
        #try:
        vmPoints.append(np.mean(data[i:i+vmWin]))
        if comp(detectionData[i]-bsl,threshold):
            xOnsets.append(i)
            eventCounter+=1
            while i<len(detectionData) and comp(detectionData[i]-bsl,(threshold-noiseSafety)):
                i+=1                
        else:
            i+=1
    return np.array(xOnsets), np.array(vmPoints)

# Get data
data = ndaq.get_data()
if len(data)>1000: data=[data]  # hack for when there is only one trace
items = ndaq.get_items()
dt = items[0].attrs['dt']

# Detect events and get measures
ap = int(AP_time/dt-AP_winCut/dt)
numbers, times, eventOnsets = [], [], []
for d in data:
    # Detect
    onset, vpoints = detect(d)
    #print(onset)
    # Select
    #i = vpoints[0:ap]<vm
    i = d[0:ap]<vm
    if np.sum(i)>0:
      l = np.arange(0,len(i))
      xpoint = l[i][-1]
      a = onset[onset>xpoint]
      events = a[a<ap]
      # Measure
      if len(events)>0:
        numbers.append(len(events))
        times.append(AP_time - events[-1]*dt)
        eventOnsets.append(AP_time - events*dt)

# Save data
print(np.mean(numbers), np.mean(times))
ndaq.store_data(np.array(numbers), name='numbers')
ndaq.store_data(np.array(times), name='last_times')
ndaq.store_data(list(eventOnsets), name='onsets')

