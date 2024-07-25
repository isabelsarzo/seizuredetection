import pandas as pd
from load_data import readHDF5, readC3D
from processing_tools import preprocess

def RMS(data):
    return None

def ZCR(data):
    return None

def medFreq(data):
    return None

def variance(data):
    return None

def coherence(data):
    return None

def iEMG(data):
    return None

def relativePower(data):
    return None

def extractFeatures(data, sliding_window, overlap, fs=1000):
    window_size = sliding_window * fs   # nb of samples in each window
    overlap_size = overlap * fs         # nb of overlapping samples in each window
    start = 0

    # Initialize features
    rms = []
    zcr = []
    mf = []
    var = []
    coher = []
    iemg = []
    rpower = []

    while start + window_size <= len(data):
        current_window = data.iloc[start : (start + window_size)]

        rms = rms.append(RMS(current_window))
        zcr = zcr.append(ZCR(current_window))
        mf = mf.append(medFreq(current_window))
        var = var.append(variance(current_window))
        coher = coher.append(coherence(current_window)) # TODO: adapt nb of columns, it is NOT in all channels
        iemg = iemg.append(iEMG(current_window))
        rpower = rpower.append(relativePower(current_window))

        start = (start + window_size) - overlap_size

    features_dict = {'RMS': rms, 
                     'ZCR': zcr,
                     'MF': mf,
                     'VAR': var,
                     'CH': coher,
                     'iEMG': iemg,
                     'RP': rpower}
    
    features = pd.DataFrame(features_dict)
    return features
