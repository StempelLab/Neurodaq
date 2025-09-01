# Align video and doric data by interpolating datasets to same timebase
# (currently the video rate, 50 fps)
# cursors can be used to select part of the doric AI channels, for when there
# are multiple doric runs in the same .tdms

import os
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from widgets import h5Item
from console import utils as ndaq
from scipy.interpolate import interp1d

# TEMP - get doric data
root = browser.ui.workingDataTree.invisibleRootItem()
folder = browser.currentFolder
#folder = '/Volumes/science-data-home/PAG_project/raw_data/doric_scope/15SEP29_Doric/65910_t2/'
#fname = '69736_t10_ROIs.txt'
for f in os.listdir(folder): 
    if os.path.splitext(f)[1]=='.txt': fname = f

d = np.loadtxt(folder+'/'+fname)
#d = np.vstack((d, np.ones(d.shape[1])))
parent = h5Item([str('doric')])
for i in range(d.shape[1]-1):
    child = h5Item([str('data_'+str(i))])
    child.data = np.array(d[:,i+1])
    parent.addChild(child)
root.addChild(parent)

# Get cursors if there are any
cursors = False
if browser.ui.dataPlotsWidget.cursor:
    cursors = True
    c1, c2 = ndaq.get_cursors()

# Get data
visual = False
audio = False
root = browser.ui.workingDataTree.invisibleRootItem()
for i in range(root.childCount()):
    item = root.child(i)
    if 'AI' in item.text(0):
        videoFrames = aux.getChild(item, '0').data
        doricFrames = aux.getChild(item, '1').data
    elif 'Coordinates' in item.text(0):
        trackingItem = item
    elif 'doric' in item.text(0):
        doricItem = item
    elif 'Visual' in item.text(0):
        visualItem = item
        visual = True
    elif 'Audio' in item.text(0):
        audioItem = item
        audio = True   

# Get video frames onset
i = videoFrames>3.0
dframes = np.diff(np.asarray(i, dtype=int))
counter = np.arange(0,len(dframes))
videoFrameIndex = counter[dframes==1] * 1./10000  #sec
videoIFI = np.diff(videoFrameIndex).mean()  
print(len(videoFrameIndex), 'video frame onsets detected with', videoIFI, 'sec IFI')

# Get doric frames onset
if cursors:
    doricWorkingFrames = np.zeros(len(doricFrames))
    doricWorkingFrames[c1:c2] = doricFrames[c1:c2]
else:
    doricWorkingFrames = doricFrames
i = doricWorkingFrames>3.0
dframes = np.diff(np.asarray(i, dtype=int))
counter = np.arange(0,len(dframes))
doricFrameIndex = counter[dframes==1] * 1./10000  #sec
doricIFI = np.diff(doricFrameIndex).mean() 
print(len(doricFrameIndex), 'doric frame onsets detected with', doricIFI, 'sec IFI')

# Interpolate all datasets to 50 fps
dt = 0.02 # sec
for i in range(trackingItem.childCount()):
    # item = trackingItem.child(i)
    # xvector = videoFrameIndex
    # print(len(xvector), len(item.data))
    # data = item.data  
    # f = interp1d(xvector, data)
    # xtime = np.linspace(xvector[0], xvector[-1], num=xvector[-1]/dt, endpoint=False)
    # item.data = f(xtime)
    item.attrs['dt'] = dt*1000
    #item.attrs['timeStamp'] = videoFrameIndex

visual = False
if visual:
  for i in range(visualItem.childCount()):
    item = visualItem.child(i)
    if 'Names' not in item.text(0):
        xvector = videoFrameIndex
        print(item.text(0), len(xvector), len(item.data))
        #if 'Indices' in item.text(0): xvector=xvector[1:]
        xvector = xvector[:-1]
        f = interp1d(xvector, item.data)
        xtime = np.linspace(xvector[0], xvector[-1], num=xvector[-1]/dt, endpoint=False)
        item.data = f(xtime)
        item.attrs['dt'] = dt*1000
        #item.attrs['timeStamp'] = videoFrameIndex

audio = False
if audio:
  for i in range(audioItem.childCount()):
    item = audioItem.child(i)
    if 'Names' not in item.text(0):
        xvector = videoFrameIndex
        print(len(xvector), len(item.data))
        f = interp1d(xvector, item.data)
        xtime = np.linspace(xvector[0], xvector[-1], num=xvector[-1]/dt, endpoint=False)
        item.data = f(xtime)
        item.attrs['dt'] = dt*1000

for i in range(doricItem.childCount()):
    # coerces times to nearest multiple of dt
    item = doricItem.child(i)
    xvector = doricFrameIndex[2:-1]   #doric drops 2 frames at the start and 1 at the end
    xvector[0] = np.ceil((xvector[0]-np.remainder(xvector[0], dt))*100)/100.
    xvector[-1] = np.ceil((xvector[-1]-np.remainder(xvector[-1], dt))*100)/100.
    print(len(xvector), len(item.data))
    f = interp1d(xvector, item.data)
    xtime = np.linspace(xvector[0], xvector[-1], num=(xvector[-1]-xvector[0])/dt, endpoint=False)    
    padStart = np.zeros(xvector[0]/dt)
    padEnd = np.zeros(len(videoFrameIndex)-xvector[-1]/dt)
    item.data = np.concatenate((padStart, f(xtime), padEnd))
    item.attrs['dt'] = dt*1000
    #item.attrs['timeStamp'] = doricFrameIndex[2:-1] 







