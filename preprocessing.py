from scipy.signal import butter, sosfilt

def timerange(data, startTime, endTime):
    """
    Extracts a subset of the dataframe containing rows within a specified time interval.

    Args:
    -----------------------------------------------------------------
    -data: dataframe from which the specified time interval will be extracted. 
    -startTime: str, start timestamp of the time interval in the format 'yyyy-mm-dd HH:MM:SS'.
    -endTime: str, end timestamp of the time interval in the format 'yyyy-mm-dd HH:MM:SS'.

    Returns:
    -----------------------------------------------------------------
    -datarange: new dataframe containing only the rows within the specified time interval.

    """
    datarange = data[startTime : endTime]
    return datarange

def lowpass(data, cutoff):
    """
    Designs and applies a digital 2nd order lowpass butterworth filter.

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the data to be filtered.
    -cutoff: int, cutoff frequency (Hz) at which the gain drops -3dB.

    Returns:
    -----------------------------------------------------------------
    -data_lp: dataframe containing the filtered data. 

    """
    lpass_design = butter(2, cutoff, 'lowpass', fs=1000, output='sos')
    data_lp = sosfilt(lpass_design, data)
    return data_lp

def highpass(data, cutoff):
    """
    Designs and applies a digital 2nd order highpass butterworth filter.

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the data to be filtered.
    -cutoff: int, cutoff frequency (Hz) at which the gain drops -3dB.

    Returns:
    -----------------------------------------------------------------
    -data_hp: dataframe containing the filtered data. 

    """
    hpass_design = butter(2, cutoff, 'highpass', fs=1000, output='sos')
    data_hp = sosfilt(hpass_design, data)
    return data_hp

def bandpass(data, cutoffs):
    """
    Designs and applies a digital 2nd order bandpass butterworth filter.

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the data to be filtered.
    -cutoffs: length-2 sequence, cutoff frequencies (Hz) at which the gain drops -3dB.

    Returns:
    -----------------------------------------------------------------
    -data_bp: dataframe containing the filtered data. 

    """
    bpass_design = butter(2, cutoffs, 'bandpass', fs=1000, output='sos')
    data_bp = sosfilt(bpass_design, data)
    return data_bp

def notch(data, cutoffs):
    """
    Designs and applies a digital 2nd order bandstop (notch) butterworth filter.

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the data to be filtered.
    -cutoffs: length-2 sequence, cutoff frequencies (Hz) at which the gain drops -3dB.

    Returns:
    -----------------------------------------------------------------
    -data_notch: dataframe containing the filtered data. 

    """
    notch_design = butter(2, cutoffs, 'bandstop', fs=1000, output='sos')
    data_notch = sosfilt(notch_design, data)
    return data_notch

def preprocess(data, hp_cutoff, notch_cutoffs):
    """
    Applies the established pre-processing pipeline: 
        1. Highpass filter
        2. Notch filter

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the data to be filtered.
    -hp_cutoff: int, cutoff frequency (Hz) for the highpass filter.
    -notch_cutoffs: length-2 sequence, cutoff frequencies (Hz) for bandstop filter.

    Returns:
    -----------------------------------------------------------------
    -data_filtered: dataframe containing the filtered data. 

    """ 
    # High-pass filter
    print("FILTERING - HIGHPASS")
    data_hp = data.apply(lambda x: highpass(x, hp_cutoff), axis=0)

    # Notch filter
    print("FILTERING - BANDSTOP")
    data_filtered = data_hp.apply(lambda x: notch(x, notch_cutoffs), axis=0)
    return data_filtered
