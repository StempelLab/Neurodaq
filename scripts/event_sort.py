# Sort events
#
# Select item with events to start

import numpy as np
import matplotlib.pylab as plt
from console import utils as ndaq

# Get data
item =  browser.ui.workingDataTree.selectedItems()[0]

# Iterate events and get onsets and traces
data, onsets = [], []
for c in range(item.childCount()):
    onsets.append(item.child(c).attrs['onset'])
    data.append(item.child(c).data)

# Get dt
dt = item.child(1).attrs['dt']

# Sort by baseline Vm
def vm_sort(onset, bsl, limits):
    # onset and bsl is time in ms, limits is tuple with (vmin, vmax)
    dataSort = []
    bsl = round(bsl/dt)
    onset = round(onset/dt)
    for d in data:
        vm = np.mean(d[onset-bsl:onset])
        if vm>limits[0] and vm<limits[1]:
            dataSort.append(d)
    dataSort = np.array(dataSort)
    plt.plot(dataSort.mean(axis=0))
    return dataSort

# Select events based on inter-event interval
def isi_sort(dur):
    # dur is isi in ms
    eventSort = []
    dur = round(dur/dt)
    currentEvent = data[0]
    currentOnset = onsets[0]
    e = 1
    while e<len(onsets):
        limit = currentOnset+dur
        if onsets[e]<limit:
            currentEvent = data[e]
            currentOnset = onsets[e]
            e+=1
        else:
            #eventSort.append(currentEvent[0:dur])
            eventSort.append(currentEvent)
            currentEvent = data[e]
            currentOnset = onsets[e]
            e+=1
    eventSort = np.array(eventSort)
    plt.plot(eventSort.mean(axis=0))
    return eventSort

# Baseline and average without plotting
def avg(data):
    mData = np.mean(data, axis=0)
    return mData

def baseline(onset, bsl, data):
    bsl = round(bsl/dt)
    onset = round(onset/dt)
    data = np.array(data)
    for n in range(len(data)):
        b = np.mean(data[n,onset-bsl:onset])
        data[n] = data[n]- b
    return data

# Get rid of negative/positive going events
def neg(data, limit):
    # limit is fraction of min or max
    dataClean, dataNorm = [], []
    for n in data:
        epeak = n[0:20/0.02].max()
        if n.min()>-limit[0]*epeak and n.max()<limit[1]*epeak:
            dataClean.append(n)
            dataNorm.append(n/epeak)
    return dataClean, dataNorm

# Run
#result = vm_sort(20,2, (-75,-10))
result = isi_sort(10)  #100
result = baseline(10,5,result)
result1, result2 = neg(result, (1.2,1.2))  #(0.2,1.5)
#result = avg(result)


# Save
ndaq.store_data(result1, name='events_clean', attrs={'dt':dt})
ndaq.store_data(result2, name='events_norm', attrs={'dt':dt})
