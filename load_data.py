import pandas as pd
from config import temp_path, perm_path # type: ignore
import argparse

def load_data(patient, date, shift, batch, hrIdx, folder, modality):
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
    print("Loading data...")
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

    # Convert 'Time' column to datetime and set it as index
    data_ds.index = pd.to_datetime(data_ds.index, format='%d-%b-%Y %H:%M:%S.%f')
    return data_ds, time_s

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generate time-stamps")
    parser.add_argument('patient', type=int, help="The patient number/code")
    parser.add_argument('date', type=int, help="Date of recording in format yyyymmdd")
    parser.add_argument('shift', type=str, help="D, A, or N shift")
    parser.add_argument('batch', type=int, help="Batch index of recordings from same shift")
    parser.add_argument('hrIdx', type=int, help="Specific hour within the continuous rec hrs or 0 for all")
    parser.add_argument('folder', type=str, help="Location of files, temp or perm")
    parser.add_argument('modality', type=str, help="emg, acm, or both")

    args = parser.parse_args()

    data_ds, time_s = load_data(args.patient, args.date, args.shift, args.batch, args.hrIdx, args.folder, args.modality)