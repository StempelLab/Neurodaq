""" Filtering functions taken from Acq4: 

https://github.com/acq4/acq4 (Luke Campagnola)

Some of the functions have been slightly modified to 
adapt to the NeuroDAQ environment.
"""

import numpy as np

def applyFilter(data, b, a, padding=100, bidir=True):
    """Apply a linear filter with coefficients a, b. Optionally pad the data before filtering
    and/or run the filter in both directions."""
    try:
        import scipy.signal
    except ImportError:
        raise Exception("applyFilter() requires the package scipy.signal.")
    
    d1 = data.view(np.ndarray)
    
    if padding > 0:
        d1 = np.hstack([d1[:padding], d1, d1[-padding:]])
    
    if bidir:
        d1 = scipy.signal.lfilter(b, a, scipy.signal.lfilter(b, a, d1)[::-1])[::-1]
    else:
        d1 = scipy.signal.lfilter(b, a, d1)
    
    if padding > 0:
        d1 = d1[padding:-padding]
    return d1
    
def besselFilter(data, cutoff, order=1, dt=None, btype='low', bidir=True):
    """return data passed through bessel filter"""
    try:
        import scipy.signal
    except ImportError:
        raise Exception("besselFilter() requires the package scipy.signal.")
    
    if dt is None:
        try:
            tvals = data.xvals('Time')
            dt = (tvals[-1]-tvals[0]) / (len(tvals)-1)
        except:
            dt = 1.0    
    b,a = scipy.signal.bessel(order, cutoff * dt, btype=btype)    
    return applyFilter(data, b, a, bidir=bidir)


def butterworthFilter(data, wPass, wStop=None, gPass=2.0, gStop=20.0, order=1, dt=None, btype='low', bidir=True):
    """return data passed through bessel filter"""
    try:
        import scipy.signal
    except ImportError:
        raise Exception("butterworthFilter() requires the package scipy.signal.")
    
    if dt is None:
        try:
            tvals = data.xvals('Time')
            dt = (tvals[-1]-tvals[0]) / (len(tvals)-1)
        except:
            dt = 1.0
    
    if wStop is None:
        wStop = wPass * 2.0
    ord, Wn = scipy.signal.buttord(wPass*dt*2., wStop*dt*2., gPass, gStop)
    b,a = scipy.signal.butter(ord, Wn, btype=btype) 
    return applyFilter(data, b, a, bidir=bidir)


def rollingSum(data, n):
    d1 = data.copy()
    d1[1:] += d1[:-1]  # integrate
    d2 = np.empty(len(d1) - n + 1, dtype=data.dtype)
    d2[0] = d1[n-1]  # copy first point
    d2[1:] = d1[n:] - d1[:-n]  # subtract
    return d2


def mode(data, bins=None):
    """Returns location max value from histogram."""
    if bins is None:
        bins = int(len(data)/10.)
        if bins < 2:
            bins = 2
    y, x = np.histogram(data, bins=bins)
    ind = np.argmax(y)
    mode = 0.5 * (x[ind] + x[ind+1])
    return mode
    
def modeFilter(data, window=500, step=None, bins=None):
    """Filter based on histogram-based mode function"""
    d1 = data.view(np.ndarray)
    vals = []
    l2 = int(window/2.)
    if step is None:
        step = l2
    i = 0
    while True:
        if i > len(data)-step:
            break
        vals.append(mode(d1[i:i+window], bins))
        i += step
            
    chunks = [np.linspace(vals[0], vals[0], l2)]
    for i in range(len(vals)-1):
        chunks.append(np.linspace(vals[i], vals[i+1], step))
    remain = len(data) - step*(len(vals)-1) - l2
    chunks.append(np.linspace(vals[-1], vals[-1], remain))
    d2 = np.hstack(chunks)
    return d2

def denoise(data, radius=2, threshold=4):
    """Very simple noise removal function. Compares a point to surrounding points,
    replaces with nearby values if the difference is too large."""
    
    
    r2 = radius * 2
    d1 = data.view(np.ndarray)
    d2 = d1[radius:] - d1[:-radius] #a derivative
    #d3 = data[r2:] - data[:-r2]
    #d4 = d2 - d3
    stdev = d2.std()
    #print("denoise: stdev of derivative:", stdev)
    mask1 = d2 > stdev*threshold #where derivative is large and positive
    mask2 = d2 < -stdev*threshold #where derivative is large and negative
    maskpos = mask1[:-radius] * mask2[radius:] #both need to be true
    maskneg = mask1[radius:] * mask2[:-radius]
    mask = maskpos + maskneg
    d5 = np.where(mask, d1[:-r2], d1[radius:-radius]) #where both are true replace the value with the value from 2 points before
    d6 = np.empty(d1.shape, dtype=d1.dtype) #add points back to the ends
    d6[radius:-radius] = d5
    d6[:radius] = d1[:radius]
    d6[-radius:] = d1[-radius:]
    return d6

def adaptiveDetrend(data, x=None, threshold=3.0):
    """Return the signal with baseline removed. Discards outliers from baseline measurement."""
    try:
        import scipy.signal
    except ImportError:
        raise Exception("adaptiveDetrend() requires the package scipy.signal.")
    
    if x is None:
        x = data.xvals(0)
    
    d = data.view(np.ndarray)
    
    d2 = scipy.signal.detrend(d)
    
    stdev = d2.std()
    mask = abs(d2) < stdev*threshold
    #d3 = where(mask, 0, d2)
    #d4 = d2 - lowPass(d3, cutoffs[1], dt=dt)
    
    lr = scipy.stats.linregress(x[mask], d[mask])
    base = lr[1] + lr[0]*x
    d4 = d - base
    return d4
    

def histogramDetrend(data, window=500, bins=50, threshold=3.0, offsetOnly=False):
    """Linear detrend. Works by finding the most common value at the beginning and end of a trace, excluding outliers.
    If offsetOnly is True, then only the offset from the beginning of the trace is subtracted.
    """
    
    d1 = data.view(np.ndarray)
    d2 = [d1[:window], d1[-window:]]
    v = [0, 0]
    for i in [0, 1]:
        d3 = d2[i]
        stdev = d3.std()
        mask = abs(d3-np.median(d3)) < stdev*threshold
        d4 = d3[mask]
        y, x = np.histogram(d4, bins=bins)
        ind = np.argmax(y)
        v[i] = 0.5 * (x[ind] + x[ind+1])
        
    if offsetOnly:
        d3 = data.view(np.ndarray) - v[0]
    else:
        base = np.linspace(v[0], v[1], len(data))
        d3 = data.view(np.ndarray) - base   
    return d3
    

def removePeriodic(data, f0=60.0, dt=None, harmonics=10, samples=4, magScale=0.1):

    ft = np.fft.fft(data)
    
    ## determine frequencies in fft data
    df = 1.0 / (len(data) * dt)
    freqs = np.linspace(0.0, (len(ft)-1) * df, len(ft))
    
    ## flatten spikes at f0 and harmonics
    for i in xrange(1, harmonics + 2):
        f = f0 * i # target frequency
        
        ## determine index range to check for this frequency
        ind1 = int(np.floor(f / df)) - (samples/2)
        ind2 = int(np.ceil(f / df)) + (samples/2-1)
        if ind1 > len(ft)/2.:
            print(f, 'breaking')
            break
        mag = (abs(ft[ind1-1]) + abs(ft[ind2+1])) * 0.5
        mag = mag * magScale
        for j in range(ind1, ind2+1):
            phase = np.angle(ft[j])   ## Must preserve the phase of each point, otherwise any transients in the trace might lead to large artifacts.
            re = mag * np.cos(phase)
            im = mag * np.sin(phase)
            ft[j] = re + im*1j
            ft[len(ft)-j] = re - im*1j
            
    data2 = np.fft.ifft(ft).real
    return data2
    
    
