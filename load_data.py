import pandas as pd
import c3d
import warnings
import numpy as np
from config import temp_path, perm_path # type: ignore
from TSGv3 import generate_timestamps   # type: ignore

warnings.filterwarnings("ignore", module="c3d.c3d")

class OriginalRecordingInfo:
    # TODO: write explanation of attributes
    def __init__(self, data, time):
        self.fs = 1 / (time[1] - time[0])
        self.samples = len(data)
        self.channels = len(data.columns)
        self.startTime = data.index[0]
        self.endTime = data.index[-1]
        self.duration = time[-1]

def readHDF5(patient, date, shift, batch, hrIdx, folder, modality):
    """
    Loads EMG-ACM data (with timestamps) from an HDF5 file and downsamples it

    Args
    -------------------------------
    -patient: patient's assigned number/code without the 'p'.
    -date: date that appears in the file name in the format yyyymmdd.
    -shift: either 'D' (day/morning shift), 'A' (afternoon shift), or 'N' (night shift) as appears in file name.
    -batch: recording batch number as appears in file name. Note that files from the same date and shift have the same batch number.
    -hrIdx: int, hour index within the number of continuous recording hours. 0 to load complete recording.
    -folder: either 'temp' (temporary folder) or 'perm' (permanent folder), depending on the location of the file.
    -modality: either 'emg' (get EMG data only), 'acm' (get ACM data only), or 'both' (get both EMG and ACM data).

    Returns
    -------------------------------
    -data_ds: dataframe containing the downsampled data as specified by input arguments. Note: The timestamps are returned as datetime objects, not strings.
    -time_s: numpy array containing the equivalent time in seconds (to use as reference in the EMG and Motion Tools software). Note: should have the same nb of rows as data_ds

    """
    print("Loading HDF5 data...")

    # Check the location of the file to load
    if folder == 'temp':
        path = temp_path    
    elif folder == 'perm':
        path = perm_path

    # Load .h5 file
    dirpath = path / f"p{patient}"
    file_name = f"p{patient}_{date}_{shift}_{batch}.h5"
    file = dirpath / file_name

    if hrIdx == 0:
        dataframes = []
        with pd.HDFStore(file, mode='r') as store:
            keys = store.keys()
            nkeys = len(keys)
            for i in range(1, nkeys + 1):
                df = pd.read_hdf(file, f"Hour{i}")
                dataframes.append(df)
        data = pd.concat(dataframes)      
    else:
        data = pd.read_hdf(file, f"Hour{hrIdx}")

    # Extract time in seconds (for Cometa software)
    time_s = data['sec'].values
    time_s = time_s[::2]  # downsample by a factor of 2
    
    # Delete the 'sec' column from the dataframe
    data = data.drop(columns=['sec'])

    # Extract either only EMG, only ACM, or both
    if modality == 'emg':
        data = data.iloc[:, 0:8] 
    elif modality == 'acm':
        data = data.drop(data.columns[0:8], axis=1)

    # Downsample data by a factor of 2
    data_ds = data.iloc[::2, :].copy()

    # Convert 'Time' column to datetime 
    data_ds.index = pd.to_datetime(data_ds.index, format='%d-%b-%Y %H:%M:%S.%f')

    return data_ds, time_s

def readC3D(patient, date, shift, batch, idx, folder, modality):
    # TODO: write docstring
    # TODO: time how long it takes to read the file and generate the timestamps
    # TODO: make github repository private so that you can upload your code
    print("Loading C3D data...")

    # Check the location of the file to load
    if folder == 'temp':
        path = temp_path    
    elif folder == 'perm':
        path = perm_path

    # Load .c3d file
    dirpath = path / f"p{patient}"
    file_name = f"p{patient}_{date}_{shift}_{batch}_{idx}.c3d"
    file = dirpath / file_name

    with open(file, 'rb') as c3dfile:
        frames = c3d.Reader(c3dfile)
        analog_samples = []
        for i, points, analog in frames.read_frames():
            analog_transposed = np.array(analog).T
            analog_samples.append(analog_transposed)

    # Concatenate the samples stored in frames
    all_analog_samples = np.concatenate(analog_samples, axis=0)

    # Convert to dataframe
    data_analog = pd.DataFrame(all_analog_samples, columns=frames.analog_labels)

    # Order columns
    new_order = [0, 4, 8, 12, 16, 20, 24, 28,
                1, 5, 9, 13, 17, 21, 25, 29,
                2, 6, 10, 14, 18, 22, 26, 30,
                3, 7, 11, 15, 19, 23, 27, 31]
    data = data_analog.iloc[:, new_order]
    data.columns = data.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    # Remove zero-padding
    data = data.apply(lambda x: np.trim_zeros(x, 'b'), axis=0)

    # Generate time axis (units = seconds) as in EMG and Motion Tools
    T = 1 / frames.analog_rate      # period in seconds
    dur = (len(data) - 1) * T       # duration in seconds
    time = np.linspace(0.0, dur, num=len(data), dtype=float)

    # Generate timestamps
    timestamps = generate_timestamps(file, time)
    data.index = timestamps
    data.index.name = 'Time-stamps'

    # Retrieve original recording information
    rawInfo = OriginalRecordingInfo(data, time)

    # Extract either only EMG, only ACM, or both
    if modality == 'emg':
        data = data.iloc[:, 0:8] 
    elif modality == 'acm':
        data = data.drop(data.columns[0:8], axis=1)

    # Downsample data by a factor of 2
    data_ds = data.iloc[::2, :].copy()
    time_ds = time[::2]

    # Convert timestamps to datetime 
    data_ds.index = pd.to_datetime(data_ds.index, format='%d-%b-%Y %H:%M:%S.%f')
    
    return data_ds, time_ds, rawInfo