import os
import numpy as np
import h5py
from nptdms import TdmsFile
from ..acq4 import filterfuncs as acq4filter
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
import neo
import quantities as pq
from OpenElectrophy.timefrequency import TimeFreq
from OpenElectrophy import neo_to_oe, open_db

class Probe():
    """
    Class for loading, displaying and analysing probe data,
    and matching video data from .tdms files    
    
    Point to a folder with the .nex files and a single .tdms file
    """
    
    def __init__(self, folder):
        self.folder = folder    
        self.tdms = None
    
    def load_nex(self, channels=np.arange(1,16)):
        """ Channels is a list of channels to read
        
        Read neo segments
        """
        basename = 'SE-CSC-RAW-Ch'
        chnOrder = [12, 2, 14, 4, 6, 3, 8, 1, 10, 7, 5, 11, 9, 15, 13] # to match probe geometry
        self.nexReaders, self.nexSegs = [], []
        for chn in channels:
            fname = basename + str(chnOrder[chn-1]) + '_.nex'
            print('Reading', fname, '....')
            try:
                r = neo.io.NeuroExplorerIO(filename=(self.folder + fname))
                self.nexReaders.append(r) 
                self.nexSegs.append(r.read_segment(lazy=False, cascade=True))
            except IOError:
                print('File', fname, 'not found')
    
    def load_tdms(self):
        """ Looks for .tdms files in folder and loads the first one
        it finds
        """
        for fname in os.listdir(self.folder):
            ext = os.path.splitext(fname)[1]            
            if ext=='.tdms': self.tdms = TdmsFile(self.folder+fname)
        if not self.tdms: print('Tdms file not found')

    def load_frameSignal(self):
        """ Loads analog input with a TTL high on the onset of each
        video frame
        """
        fname = 'Analog Input Ch16_.nex'
        try:
            self.frameReader = neo.io.NeuroExplorerIO(filename=(self.folder + fname)) 
            self.framesSeg = self.frameReader.read_segment(lazy=False, cascade=True)
        except IOError:
            print('File', fname, 'not found')
       
    def get_frameIndex(self):
        """ Get datapoint indices of analog signals that correspond
        to frame onsets 
        
        Cutting the artefact at the beginning of the frames trace for
        TTL detection causes an offset between this and the other analog
        signals, stored for correction in self.framesOffset
        """
        frames = np.array(self.framesSeg.analogsignals[0])
        # Get rid of probe starting artefact to allow TTL detection
        icounter = np.arange(0,len(frames))
        self.framesOffset = icounter[frames<(-1000)][-1]+100
        frames = frames[self.framesOffset:]
        # Get the start of each frame
        dframes = np.diff(frames)
        icounter = np.arange(0,len(dframes))
        self.framesIndex = icounter[dframes>1000]
        self.framesSeg, frames = None, None

    def get_dataWindow(self, win=(0,0), tdms=False):
        """ Load data segments and cut to desired
        time window. 
        
        Option to get the matching window for tdms
        data (position and spot profile)
        
        win is the window (tuple), default is to get everything 
        """
        # Get analog signals
        print('Getting data windows....')
        self.dataWin = []
        if win==(0,0):
            istart = self.framesIndex[0]  + self.framesOffset
            iend = self.framesIndex[len(self.framesIndex)-1] + self.framesOffset
        else:
            istart = self.framesIndex[win[0]] + self.framesOffset
            iend = self.framesIndex[win[1]] + self.framesOffset           
        for seg in self.nexSegs:
            data = np.array(seg.analogsignals[0])         
            self.dataWin.append(data[istart:iend])
        seg, data = None, None
        # Get tdms
        if tdms:
            try:
                self.pos = self.tdms.object('Real-time Coordinates', 'X-Vertical').data[win[0]:win[1]]    
                self.spot = self.tdms.object('Visual  Stimulation', 'Spot Diameter').data[win[0]:win[1]]
            except AttributeError:
                print('No TDMS data loaded')

    def get_probeData(self):
        """ Get all probe data
        """
        self.data = []
        for seg in self.nexSegs:
            self.data.append(np.array(seg.analogsignals[0]))         


    def get_timeFreq(self, data, f_start, f_stop, deltafreq):
        """ Calculate spectogram for data and store tfr object
        Data can be a list of signals
        
        Note that sampling rates are hardcoded at the moment
        """
        print('Calculating spectograms....')
        self.tfrData = []
        for signal in data:
            anasig = neo.AnalogSignal(signal, units='V', t_start=0*pq.s, sampling_rate=30000*pq.Hz)
            self.tfrData.append(TimeFreq(anasig, f_start=f_start, f_stop=f_stop, deltafreq=deltafreq,
                                f0=2.5,  sampling_rate=f_stop*2.))

    #def data_filter(self, data):











