import pandas as pd
from load_data import load_data
from plot_tools import plotEMG, plotFreq
from scipy.signal import butter, sosfilt

def highpass(data, cutoff):
    filtdesign = butter(2, cutoff, 'highpass', fs=1000, output='sos')
    data_hp = sosfilt(filtdesign, data)
    return data_hp

def preprocess(data, hp_cutoff):
    time = data.index
    channels = data.columns
    
    # High-pass filter
    print("FILTERING - HIGHPASS")
    data_hp = data.apply(lambda x: highpass(x, hp_cutoff), axis=0)

    # Notch filter
    # ... TODO: design and apply bandstop filter

    # Recreate dataframe
    data_f = pd.DataFrame(data_hp, index=time, columns=channels)

    return data_f

data, time_s = load_data(308, 20240703, 'A', 44, 5, 'temp', 'emg')
data_f = preprocess(data, 100)

plotEMG(data, 'all', 3500, 0, "Original")
signal = data.iloc[:, 1].values
channel = "Original Left Trapeze"
plotFreq(signal, channel, "FreqOriginal")

plotEMG(data_f, 'all', 3500, 0, "Filtered")
signal_hp = data_f.iloc[:, 1].values
channel2 = "Filtered Left Trapeze"
plotFreq(signal_hp, channel2, "FreqFiltered")


