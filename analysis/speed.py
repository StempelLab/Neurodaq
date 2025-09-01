# temp script to tranform velocity traces into something useful

import numpy as np
from analysis import smooth
from console import utils as ndaq

# Parameters
posThs = 1.66
negThs = 1.62
final_smth_window = 100

# Get data and items
data = ndaq.get_data()
item = ndaq.get_items()
dt = item[0].attrs['dt']

# Smooth
data = smooth.smooth(data, window_len=4, window='hanning')

# Threshold detection functions
compPositive = lambda a, b: a > b
compNegative = lambda a, b: a < b

# Go through data
i = 0
eStart, eEnd = [], []
while i<len(data):
    if compPositive(data[i], posThs):
        eStart.append(i)
        while i<len(data) and compPositive(data[i], posThs-0.02):
            i+=1
        eEnd.append(i-1)
    elif compNegative(data[i], negThs):
        eStart.append(i)
        while i<len(data) and compNegative(data[i], negThs+0.02):
            i+=1
        eEnd.append(i-1)
    else:
        i+=1

# Get mean value of 'reading' events
speed, xpoints = [], []
for e in np.arange(0, len(eStart)):
    x = round((eStart[e]+eEnd[e])/2)
    xpoints.append(x)
    speed.append(data[x])
    #x = np.array([eStart[e], eEnd[e]])
    #y = np.array([data[eStart[e]], data[eEnd[e]]])
    #ndaq.plot_data(x,y)

# Plot data
#xspeed = np.array(eStart)#*dt, dt)
#ndaq.plot_data(xspeed,np.array(speed), color='r', clear=True)
ndaq.plot_data(np.array(xpoints), np.array(speed), color='r', clear=True)
#xdata = np.arange(0, len(data))#*dt, dt)
ndaq.plot_data(data)




