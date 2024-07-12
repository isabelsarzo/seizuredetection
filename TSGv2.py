import os
import pandas as pd
import datetime
import pathlib
from timeit import default_timer as timer
from config import temp_path, perm_path # type: ignore
import argparse

def TSG(patient, date, shift, batch, n_files, start_idx, folder):
    """
    Generates the time-stamps for a full batch of EMG-ACM recordings acquired with the Cometa system 
    and exports them (along with the raw data) to csv files in the temporary folder. 

    Requirements:
    -Original C3D files (or the unmodified versions)
    -Text files containing the data from the C3D files exported by the EMG and Motion Tools software

    Args
    -------------------------------
    -patient: patient's assigned number/code without the 'p'.
    -date: date that appears in the file names, format yyyymmdd.
    -shift: either 'D' (day/morning shift), 'A' (afternoon shift), or 'N' (night shift) as appears in file names.
    -batch: recording batch number as appears in file names. Note that files from the same date and shift have the same batch number.
    -n_files: total number of files in the batch. This has to be equal or greater than start_idx.
    -start_idx: starting file number (usually always 1)
    -folder: either 'temp' (temporary folder) or 'perm' (permanent folder), depending on the location of the .c3d and .txt files.
    
    Returns
    -------------------------------
    None 

    """ 
    start_timer = timer()

    print("-------------------------------------")
    print("           PROCESS STARTED           ")
    print("-------------------------------------")

    patient = str(patient)
    date = str(date)
    batch = str(batch)

    for i in range(start_idx, n_files + 1):
        if folder == 'temp':
            path = temp_path
        elif folder == 'perm':
            path = perm_path
        
        # Get full path for .txt file
        #dirpath = f"{path}{patient}"
        dirpath = path / f"p{patient}"
        file_name = f"p{patient}_{date}_{shift}_{batch}_{i}.txt"
        #file = os.path.join(dirpath, file_name)
        file = dirpath / file_name

        # Load raw data
        data = pd.read_csv(file, sep='\t', skiprows=[0])

        # Get the name of the column that contains the time (seconds) of each datapoint
        time = data.columns[0]

        # Change the column name to "sec"
        if time == 'Time(s):':
            data = data.rename(columns={'Time(s):': 'sec'})
        else:
            data = data.rename(columns={'Time (s):': 'sec'})
        
        sec = data['sec'].to_numpy()

        # Get full path for .c3d file
        file_no_extension = os.path.splitext(file)[0]
        c3d_file = pathlib.Path(f'{file_no_extension}.c3d')

        if not os.path.exists(c3d_file): # Verify .c3d file existence
            print('The C3D file was not found. Make sure to save it with the same name and path as the text file.')
        else:
            print(f'FILE {i} of {n_files}:')
            print('Retrieving information...')

            # Get the last modification date-time of the .c3d file
            dt_vec = c3d_file.stat().st_mtime 
            time_stopped = datetime.datetime.fromtimestamp(dt_vec).strftime('%d-%b-%Y %H:%M:%S.%f')
            print(f'-Recording stopped at {time_stopped}')
        
            # Calculate the duration of the recording
            duration_s = sec[-1]
            print(f'-Recording duration is {duration_s} seconds')

            # Calculate the time at which the recording started
            time_started = (datetime.datetime.strptime(time_stopped, '%d-%b-%Y %H:%M:%S.%f') - datetime.timedelta(seconds=duration_s)).strftime('%d-%b-%Y %H:%M:%S.%f')
            print(f'-Recording started at {time_started}')

            # Sample frequency determination
            tf = sec[1]
            ti = sec[0]
            T = tf - ti
            fs = 1 / T
            print(f'-Sample frequency is {fs} Hz')

            print("Generating time-stamps for file...")

            # Generate time-stamp for each datapoint and use it as index in the dataframe
            data.index = pd.date_range(start=time_started, periods=len(sec), freq=pd.DateOffset(seconds=T)).strftime('%d-%b-%Y %H:%M:%S.%f')
            data.index.name = 'Time'
            
            # Get full path for output .csv file
            outpath = temp_path / f"p{patient}" / file_name
            #outfile = os.path.join(outpath, file_name)
            outfile_no_ext = os.path.splitext(outpath)[0]
            csv_file = pathlib.Path(f'{outfile_no_ext}_TimeStamps.csv')

            # Export data with time-stamps to .csv file
            data.to_csv(csv_file)
            print("Success!")

    print("-------------------------------------")
    print("            PROCESS ENDED            ")
    print("-------------------------------------")

    end_timer = timer()
    elapsed = end_timer - start_timer
    print(f'Code executed in {elapsed:.2f} seconds')
    print("-------------------------------------")

    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generate time-stamps")
    parser.add_argument('patient', type=int, help="The patient number/code")
    parser.add_argument('date', type=int, help="Date of recording in format yyyymmdd")
    parser.add_argument('shift', type=str, help="D, A, or N shift")
    parser.add_argument('batch', type=int, help="Batch index of recordings from same shift")
    parser.add_argument('n_files', type=int, help="Total number of files in batch")
    parser.add_argument('start_idx', type=int, help="File number to start TSG, usually 1")
    parser.add_argument('folder', type=str, help="Location of files, temp or perm")

    args = parser.parse_args()

    TSG(args.patient, args.date, args.shift, args.batch, args.n_files, args.start_idx, args.folder)