# This Python file uses the following encoding: utf-8

""" Library of functions to process tag data. Functions have to be called from
NeuroDAQ

TAGS:
A: first startle
B: flight onset
C: reaches nest
D: failed flight; point of resumed exploration/end of freeze
E: end of flight (which didn’t reach nest, e.g. to the corner)
F: freeze (in pairs of two, first start, second end of instance)
G: resumed exploration/movement, for a mouse which flees late and doesn’t freeze the whole time.
H: tail rattle
I: Immobile, has detected stimulus, but a few movements (e.g head) as opposed to ‘true' freezing?
J: video glitch
"""

import numpy as np
import re
import matplotlib.pylab as plt
from scipy.interpolate import interp1d
from console import utils as ndaq
from widgets import h5Item
from ...analysis import auxfuncs as aux
from analysis import smooth

# Functions
def getTagData(parentItem, tag):
    """Return the data associated with a specific tag
    tag is a string
    """
    tagString = 'VideoTag_' + tag
    for c in range(parentItem.childCount()):
        if parentItem.child(c).text(0)==tagString:
            return parentItem.child(c).data

def getPlotsData(items, *args):
    """ Returns data of a specified dataype for plotting.
    Results is a list

    args:
    datatype, results, mlist=None, tagTimes='relative'
    items = [protocolItem, triggerItem, frameItem]

    datatype:
    'detection-reaction': returns tuples with detection, contrast, reaction times
    'rt-plot': returns tuples with reaction times and contrast
    'failures': returns tuples with 1 or 0 and contrast
    'spot-pr': returns tuples with escape spot ([0010]) and contrast
    mlist is a list of mouse ids to include
    """

    protocolItem = items[0]
    triggerItem = items[1]
    frameItem = items[2]
    datatype = args[0]
    results = args[1]
    mlist = args[2]
    tagTimes= args[3]

    tags=['A','B','C','D','E','F','G','H','I','J','K','L']
    if tagTimes=='absolute':
        tagTimesItem = aux.getItemFromPath(['TagData', 'TagTimes_absolute'],frameItem)
    elif tagTimes=='relative':
        tagTimesItem = aux.getItemFromPath(['TagData', 'TagTimes_fromTrigger'],frameItem)

    # Build list of Tags that exist in video
    videoTags = []
    for c in range(tagTimesItem.childCount()):
        videoTags.append(str(tagTimesItem.child(c).text(0).split('_')[1]))

    # Get data from selected tag
    if datatype=='detection-reaction':
        data = []
        #if ("D" in videoTags): print("fail")
        if ("A" in videoTags):
            st = getTagData(tagTimesItem, 'A')[0]
            if st<1000.:
                data.append(st)
                data.append(int(protocolItem.text(0)[-4:-2]))
                #data.append(int(protocolItem.text(0)[-2])) # US
            if data and ("B" in videoTags) and not ("D" in videoTags):
                rt = getTagData(tagTimesItem, 'B')[0]
                if rt-st<8000.: data.append(rt)
        if data:
            results.append(tuple(data))

    if datatype=='rt-plot':
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            st = getTagData(tagTimesItem, 'A')[0]
            if (st<3000.) and ("B" in videoTags) and not ("D" in videoTags):
                rt = getTagData(tagTimesItem, 'B')[0]
                if rt-st<6000:  #8000
                    data.append(rt)#-st)
                    data.append(int(protocolItem.text(0)[-4:-2]))
                    #data.append(int(protocolItem.text(0)[-2])) # US
                    data.append(triggerItem.text(0).split('_')[1])
        if data:
            results.append(tuple(data))

    if datatype=='rt-plot_clicks':
        print('running rt-plot_clicks')
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("B" in videoTags):
            rt = getTagData(tagTimesItem, 'B')[0]
            data.append(rt)#-st)
            data.append(int(protocolItem.text(0)[-4:-2]))
            #data.append(int(protocolItem.text(0)[-2])) # US
            data.append(triggerItem.text(0).split('_')[1])
        if data:
            results.append(tuple(data))

    if datatype=='failures':
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("D" in videoTags):
                data.append(0)
                print(getTagData(tagTimesItem, 'D')[0]-getTagData(tagTimesItem, 'A')[0])
            #elif (not "B" in videoTags):
            #    data.append(0)
            else:
                data.append(1)
            data.append(int(protocolItem.text(0)[-4:-2]))
            #data.append(int(protocolItem.text(0)[-2])) # US
        if data:
            results.append(tuple(data))

    if datatype=='us-pr':
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("B" in videoTags):
                data.append(1)
            else:
                data.append(0)
            #data.append(int(protocolItem.text(0)[-4:-2]))
            data.append(int(protocolItem.text(0)[-2:]))
        if data:
            results.append(tuple(data))

    if datatype=='spot-pr':
        spotTimes = [0, 1140, 2260, 3400, 4520, 4520+1140]
        spots = np.zeros(5)
        data = []
        go = False
        mouseid = triggerItem.text(0)[7:13]
        if mlist is not None:
            if mouseid in mlist:
                go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("B" in videoTags):
                t = getTagData(tagTimesItem, 'B')[0]
                for n in range(len(spotTimes)-1):
                    if spotTimes[n] <= t <= spotTimes[n+1]: spots[n]=1
                data.append(spots)
                data.append(int(protocolItem.text(0)[-4:-2]))
                data.append(mouseid)
        if data:
            results.append(tuple(data))

    if datatype=='raster':
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("B" in videoTags):
                rt = getTagData(tagTimesItem, 'B')[0]
                speedItem = aux.getItemFromPath(['speed'],frameItem)
                if speedItem:
                    dt = speedItem.attrs['dt']
                    ydata = speedItem.data
                    if dt > 20:
                        xvector = np.arange(0,len(ydata)*dt,dt)
                        f = interp1d(xvector, ydata)
                        xtime = np.linspace(xvector[0], xvector[-1], num=xvector[-1]/20., endpoint=False)
                        ydata = f(xtime)
                    data.append(ydata[0:3200])
                    data.append(rt)
                    data.append(int(protocolItem.text(0)[-4:-2]))
        if data:
            results.append(data)

    if datatype=='speed_traces':
        data = []
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("B" in videoTags):
                rt = getTagData(tagTimesItem, 'B')[0]
                speedItem = aux.getItemFromPath(['speed'],frameItem)
                if speedItem:
                    dt = speedItem.attrs['dt']
                    ydata = speedItem.data
                    if dt > 20:
                        xvector = np.arange(0,len(ydata)*dt,dt)
                        f = interp1d(xvector, ydata)
                        xtime = np.linspace(xvector[0], xvector[-1], num=xvector[-1]/20., endpoint=False)
                        ydata = f(xtime)
                    data.append(ydata[0:3200])
                    data.append(rt)
                    data.append(int(protocolItem.text(0)[-4:-2]))
                    data.append(dt)
        if data:
            results.append(data)

    if datatype=='vigor':
        data = []
        maxSpeed = None
        spotTimes = [0, 1140, 2260, 3400, 4520, 4520+1140]
        go = False
        if mlist is not None:
            if triggerItem.text(0)[7:13] in mlist: go = True
        else:
            go = True
        if go and ("A" in videoTags):
            if ("B" in videoTags):
                rt = getTagData(tagTimesItem, 'B')[0]
                spot = np.sum([rt>s for s in spotTimes])
                if ("C" in videoTags):
                    nt = getTagData(tagTimesItem, 'C')[0]
                    escapeDur = nt-rt
                    data.append(escapeDur)
                else:
                    data.append(np.NaN)
                speedItem = aux.getItemFromPath(['speed'],frameItem)
                if speedItem:
                    dt = speedItem.attrs['dt']
                    print(dt)
                    #print(speedItem.data[10000/dt:18000/dt])
                    maxSpeed = np.max(speedItem.data[10000/dt:18000/dt])
                    data.append(maxSpeed)
                else:
                    data.append(np.NaN)
                data.append(spot)
                data.append(int(protocolItem.text(0)[-4:-2]))
                data.append(triggerItem.text(0).split('_')[1])
                print(rt, maxSpeed)
        if data:
            results.append(tuple(data))

def genMouseList(items, *args):
    """ Go through the selected items and generate a list of animal ids
    that are contained in the data. Currently assumes data are in "manual_XXX"
    and that the animal id is 6 characters.
    Starting item is triggerItem
    args: idList
    """
    try:
        item = items[1]
    except IndexError:
        return
    idlist = args[1]
    string = item.text(0)
    if 'manual' in string:
        mouseid = string[7:13]
        if mouseid not in idlist: idlist.append(mouseid)
    return idlist


def saveIdList(browser, idlist):
    """ Save mouse id list in the data tree with an item per mouse
    """
    root = browser.ui.workingDataTree.invisibleRootItem()
    listitem = h5Item(['animal_list'])
    root.addChild(listitem)
    for i in idlist:
        mouseitem = h5Item([i])
        listitem.addChild(mouseitem)

def getROIs_old(items, *args):
    """ Collate doric ROIs into a single array for plotting and converts to dfF
    Include detection and reaction times. Returns a list with array and times
    as tuple.
    args:
    results, mouse='all', tagTimes='relative'
    items = [protocolItem, triggerItem, frameItem]

    TODO: first part is duplicated from getsPlotData, sort out
    """
    protocolItem = items[0]
    frameItem = items[2]
    results = args[0]
    mouse = args[1]
    tagTimes = args[2]

    tags=['A','B','C','D','E','F','G','H','I','J']
    if tagTimes=='absolute':
        tagTimesItem = aux.getItemFromPath(['TagData', 'TagTimes_absolute'],frameItem)
    elif tagTimes=='relative':
        tagTimesItem = aux.getItemFromPath(['TagData', 'TagTimes_fromTrigger'],frameItem)

    # Build list of Tags that exist in video
    videoTags = []
    for c in range(tagTimesItem.childCount()):
        videoTags.append(str(tagTimesItem.child(c).text(0).split('_')[1]))

    # Get reaction and detection times
    rtdata = []
    #if ("D" in videoTags): print("fail")
    if ("A" in videoTags):
        st = getTagData(tagTimesItem, 'A')[0]
        if st<1000.:
            rtdata.append(st)
            rtdata.append(1) #int(protocolItem.text(0)[-4:-2]))
        if rtdata and ("B" in videoTags) and not ("D" in videoTags):
            rt = getTagData(tagTimesItem, 'B')[0]
            if rt-st<8000.: rtdata.append(rt)

    for c in range(frameItem.childCount()):
        if 'ROI' in frameItem.child(c).text(0):
            data = dfF(frameItem.child(c))
            #data = data/data[400:1000].max() # NORMALISES!!
            if (len(data)== 3500) and rtdata:
                results.append([data, tuple(rtdata)])


def getROIs(items, *args):
    """ Get all ROIs (from a specified tag align) to make average traces
    option to align to tag, if the tag is there
    args: results, align True or False, tag
    saves list with trace data, stim type, behaviour result, roi id,
    trial id, mouse day id, contrast, max speed, speed data, tag
    """
    protocolItem = items[0]
    triggerItem = items[1]
    frameItem = items[2]
    results = args[0]
    align = args[1]
    tag = args[2]
    for c in range(frameItem.childCount()):
        if 'ROI' in frameItem.child(c).text(0):
            # dF/F and Z-score
            dataDF = dfF(frameItem.child(c), zscore=False)
            #dataDF = dfF(frameItem.child(c), zscore=False)
            data = raw(frameItem.child(c))

            # Get tag
            tagTime = 20000 # if there is no tag. #changed DE 19MAR27
            tagTimesItem = aux.getItemFromPath(['TagData','TagTimes_absolute'],frameItem)
            if tagTimesItem:
                videoTags = []
                for c2 in range(tagTimesItem.childCount()):
                    videoTags.append(str(tagTimesItem.child(c2).text(0).split('_')[1]))
                if (tag in videoTags):
                    tagTime = getTagData(tagTimesItem, tag)[0]
                    #print(tagTime)
                    if align:
                        data = alignROIs(frameItem, frameItem.child(c), data, tag)
                        dataDF = alignROIs(frameItem, frameItem.child(c), dataDF, tag)
                else:
                    data = data[0:1800]  #work around DE 19MAR27
                    dataDF = dataDF[0:1800]
            # Add metadata
            metadata = protocolItem.text(0).split('_')
            triggerStr = triggerItem.text(0).split('_')
            frameStr = frameItem.text(0).split('_')
            ROIstr = frameItem.child(c).text(0)
            idROI = triggerStr[1]+triggerStr[2]+ROIstr
            idTrial = triggerStr[1]+frameStr[-1]
            idMouseDay = triggerStr[1]+triggerStr[2]
            idMouse = triggerStr[1]
            if triggerStr[-1][-2::]=='pc':
                contrast = int(triggerStr[-1][-4:-2])
            else:
                contrast = np.NaN
            maxSpeed = np.NaN
            stimTime = np.NaN
            speedData = np.ones(2400)*np.NaN #changed DE 19MAR27
            speedItem = aux.getItemFromPath(['speed'],frameItem)
            if speedItem:
                dt = speedItem.attrs['dt']
                speedData = smooth.smooth(speedItem.data,window_len=50)
                maxSpeed = np.max(speedData[int(tagTime/dt):int(tagTime/dt+2000/dt)]) #2000 might need shortening
                if align:
                    speedData = alignROIs(frameItem, frameItem.child(c), speedData, tag)
            if tagTime==20000:tagTime = np.NaN#changed DE 19MAR27
            results.append([data,metadata[0],metadata[1],idROI,
                           idTrial,idMouseDay,contrast, maxSpeed,
                           speedData, tagTime, dataDF, idMouse])

def alignROIs(frameItem, item, data, tag):
    """ Output data with data stating at tagTime - baseline
    """
    # Baseline (in ms)
    bsl = 20000.#changed DE 19MAR27
    alignedData = None
    tagTimesItem = aux.getItemFromPath(['TagData','TagTimes_absolute'],frameItem)
    if tagTimesItem is not None:
        videoTags = []
        for c in range(tagTimesItem.childCount()):
            videoTags.append(str(tagTimesItem.child(c).text(0).split('_')[1]))
        if (tag in videoTags):
            tagTime = getTagData(tagTimesItem, tag)[0] ### change tag instance here, not in getROIs
            dt = item.attrs['dt']
            dt = 33.333333333333333333333333333 #changed DE 19MAR27
            tagIndex = int(tagTime/dt)
            cutIndex = tagIndex - int(bsl/dt)
            endIndex=cutIndex+1800   #will be fine for B tags, not sure about others. #added DE 19MAR27
            alignedData = data[cutIndex:endIndex] #changed DE 19MAR27
            #alignedData = data[cutIndex::]
    if alignedData is not None:
        if len(alignedData)==0:
            print(frameItem.text(0), tagTime, tagIndex, cutIndex, dt)
        return alignedData
    else:
        return data

def dfF(dataItem, zscore=False):
    """ Convert doric data into dfF
    """
    # Baseline (in ms)
    dFbwindow = [0., 20000.] #changed DE 19MAR27. 15000-20000
    zbwindow = [0., 20000.]
    #zbwindow = [0., 10000.]
    # deal with dt and baseline
    data = dataItem.data
    #ndaq.store_data(data, name='origData', attrs={'dt': 33.33333333333})

    if len(data)<2400:  #correct any length mess ups (e.g labview acq ended too soon after trial, or 33.3 round up error)
        padded=np.ones(2400)
        padded[0:len(data)]=data
        data=padded
    if len(data)>2400:
        data=data[0:2400]

    dt = dataItem.attrs['dt']
    dt = 33.3333333333333333333333333
    dFbwindow_dt = np.array(dFbwindow)/dt
    # get df
    bsl = np.mean(data[int(dFbwindow_dt[0]):int(dFbwindow_dt[1])])
    #ndaq.store_data(bsl, name='bsl',attrs={'dt': 33.33333333333})

    #bsl = np.mean(data)
    #bsl = np.mean(data)
    dfF = data - bsl
    #ndaq.store_data(df, name='df',attrs={'dt': 33.33333333333})

    # get df/F (%)
    #data[data==0]=0.00001    #this changes the input data in the data tree!! was 1
    #dfF = df/data*100

    #ndaq.store_data(dfF, name='dfF',attrs={'dt': 33.33333333333})

    if zscore:
        zbwindow_dt = np.array(zbwindow)/dt
        zbsl = np.mean(dfF[int(zbwindow_dt[0]):int(zbwindow_dt[1])])
        zsd = np.std(dfF[int(zbwindow_dt[0]):int(zbwindow_dt[1])])
        #zbsl = np.mean(dfF)
        #zsd = np.std(dfF)
        #zbsl = np.mean(dfF)
        #zsd = np.std(dfF)
        #data[data==0]=1
        z = (dfF-zbsl)/zsd
        z = np.nan_to_num(z) #silly solution DE 19MAr27
        #ndaq.store_data(z, name='z',attrs={'dt': 33.33333333333})

        return z
    else:
        return dfF

def raw(dataItem): 
    '''get raw trace instead of df or z'''


    data = np.array(dataItem.data)
    #ndaq.store_data(data, name='raw', attrs={'dt': 33.33333333333})

    if len(data)<2400:  #correct any length mess ups (e.g labview acq ended too soon after trial, or 33.3 round up error)
        padded=np.ones(2400)
        padded[0:len(data)]=data
        data=padded
    if len(data)>2400:
        data=data[0:2400]

    #data[data==0]=0.00001    #this changes the input data in the data tree!! was 1
    return data


def test(*args):
    print(args)


def protocolIterate(selectedItems, func, funcArgs, level=''):
    """ Iterate selected protocol items (e.g.: DE_ttxxx)
    up to a specified level and run func.
    Level can be 'protocol' or 'trigger' to stop before frame items
    funcArgs is a list of args for passing to func
    """
    for protocolItem in selectedItems:
        if level=='protocol':
            items = [protocolItem]
            func(items, *funcArgs)
        else:
            for c in range(protocolItem.childCount()):
                triggerItem = protocolItem.child(c)
                if level=='trigger':
                    items = [protocolItem, triggerItem]
                    func(items, *funcArgs)
                else:
                    for c in range(triggerItem.childCount()):
                        frameItem = triggerItem.child(c)
                        items = [protocolItem, triggerItem, frameItem]
                        func(items, *funcArgs)
