import pandas as pd
from config import temp_path, perm_path # type: ignore
import argparse

def load_data(patient, date, shift, batch, file_idx, folder, modality):
    """
    Loads EMG-ACM data (with timestamps) from a CSV file and downsamples it

    Args
    -------------------------------
    -patient: patient's assigned number/code without the 'p'.
    -date: date that appears in the file name in the format yyyymmdd.
    -shift: either 'D' (day/morning shift), 'A' (afternoon shift), or 'N' (night shift) as appears in file name.
    -batch: recording batch number as appears in file name. Note that files from the same date and shift have the same batch number.
    -file_idx: file number as appears in file name (file index within the batch).
    -folder: either 'temp' (temporary folder) or 'perm' (permanent folder), depending on the location of the file.
    -modality: either 'emg' (get EMG data only), 'acm' (get ACM data only), or 'both' (get both EMG and ACM data).

    Returns
    -------------------------------
    -data_ds: dataframe containing the downsampled data as specified by input arguments.
    -time_s: numpy array containing the equivalent time in seconds (to use as reference in the EMG and Motion Tools software).

    """
    # Convert to strings
    patient = str(patient)
    date = str(date)
    batch = str(batch)
    file_idx = str(file_idx)

    # Check the location of the file to load
    if folder == 'temp':
        path = temp_path
    
    elif folder == 'perm':
        path = perm_path

    # Load .csv file
    dirpath = path / f"p{patient}"
    file_name = f"p{patient}_{date}_{shift}_{batch}_{file_idx}_TimeStamps.csv"
    file = dirpath / file_name
    data = pd.read_csv(file)

    # Extract time in seconds (for Cometa software)
    time_s = data['sec'].values
    time_s = time_s[::2]  # downsample by a factor of 2
    
    # Delete the 'sec' column from the dataframe
    data = data.drop(columns=['sec'])

    # Extract either only EMG, only ACM, or both
    if modality == 'emg':
        data = data.iloc[:, 0:9] 
    elif modality == 'acm':
        data = data.drop(data.columns[1:9], axis=1)

    # Downsample data by a factor of 2
    data_ds = data.iloc[::2, :]

    # Convert 'Time' column to datetime and set it as index
    data['Time'] = pd.to_datetime(data['Time'])
    data.set_index('Time', inplace=True)

    return data_ds, time_s

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generate time-stamps")
    parser.add_argument('patient', type=int, help="The patient number/code")
    parser.add_argument('date', type=int, help="Date of recording in format yyyymmdd")
    parser.add_argument('shift', type=str, help="D, A, or N shift")
    parser.add_argument('batch', type=int, help="Batch index of recordings from same shift")
    parser.add_argument('file_idx', type=int, help="File number within batch")
    parser.add_argument('folder', type=str, help="Location of files, temp or perm")
    parser.add_argument('modality', type=str, help="emg, acm, or both")

    args = parser.parse_args()

    data_ds, time_s = load_data(args.patient, args.date, args.shift, args.batch, args.file_idx, args.folder, args.modality)