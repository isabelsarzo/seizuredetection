import pandas as pd
from load_data import load_data
from plot_tools import plotEMG, plotFreq
from scipy.signal import butter, sosfilt

def highpass(data, cutoff):
    # TODO: write the docstring 
    hpass_design = butter(2, cutoff, 'highpass', fs=1000, output='sos')
    data_hp = sosfilt(hpass_design, data)
    return data_hp

def notch(data, cutoffs):
    # TODO: write the docstring
    notch_design = butter(2, cutoffs, 'bandstop', fs=1000, output='sos')
    data_notch = sosfilt(notch_design, data)
    return data_notch

def preprocess(data, hp_cutoff, notch_cutoffs):
    # TODO: write the docstring
    time = data.index
    channels = data.columns
    
    # High-pass filter
    print("FILTERING - HIGHPASS")
    data_hp = data.apply(lambda x: highpass(x, hp_cutoff), axis=0)
    print(f"Type of data after highpass: {type(data_hp)}")

    # Notch filter
    print("FILTERING - BANDSTOP")
    data_filtered = data_hp.apply(lambda x: notch(x, notch_cutoffs), axis=0)

    # Recreate dataframe
    data_f = pd.DataFrame(data_filtered, index=time, columns=channels)

    return data_f

data, time_s = load_data(308, 20240703, 'A', 44, 5, 'temp', 'emg')
data_f = preprocess(data, 10, [59, 61])

plotEMG(data, 'all', 3500, 0, "Original")
signal = data.iloc[:, 1].values
channel = "Original Left Trapeze"
plotFreq(signal, channel, "FreqOriginal")

plotEMG(data_f, 'all', 3500, 0, "Filtered")
signal_hp = data_f.iloc[:, 1].values
channel2 = "Filtered Left Trapeze"
plotFreq(signal_hp, channel2, "FreqFiltered")

# TODO: create a function to extract a timerange of data
