import os
import pandas as pd
import datetime
import pathlib
from timeit import default_timer as timer
from config import temp_path, perm_path

def TSG(patient, date, shift, batch, n_files, start_idx, folder):
    """
    Generates the time-stamps for a specific EMG-ACM recording acquired with the Cometa system. 
    Requirements:
    -Original C3D file (or an unmodified version)
    -Text file containing the data from the C3D file exported by the EMG and Motion Tools software

    Args
    -------------------------------
    -patient: patient's assigned number/code without the 'p'.
    -date: date that appears in the file name in the format yyyymmdd.
    -shift: either 'D' (day/morning shift), 'A' (afternoon shift), or 'N' (night shift) as appears in file name.
    -batch: recording batch number as appears in file name. Note that files from the same date and shift have the same batch number.
    -n_files:
    -start_idx:
    -folder: either 'temp' (temporary folder) or 'perm' (permanent folder), depending on the location of the file.
    
    Returns
    -------------------------------
    -data: dataframe containing the data with its corresponding time-stamps as indexes. 

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
        
        dirpath = f"{path}{patient}"
        file_name = f"p{patient}_{date}_{shift}_{batch}_{i}.txt"
        file = os.path.join(dirpath, file_name)
        #file = pathlib.Path(r'I:\Chercheurs\BouAssi_Elie\Data\Cometa\p308\p308_20240703_D_43_7.txt')
        data = pd.read_csv(file, sep='\t', skiprows=[0])
        time = data.columns[0]

        if time == 'Time(s):':
            data = data.rename(columns={'Time(s):': 'sec'})
        else:
            data = data.rename(columns={'Time (s):': 'sec'})
        
        sec = data['sec'].to_numpy()

        file_no_extension = os.path.splitext(file)[0]
        c3d_file = pathlib.Path(f'{file_no_extension}.c3d')

        # Verify C3D file existence
        if not os.path.exists(c3d_file):
            print('The C3D file was not found. Make sure to save it with the same name and path as the text file.')
        else:
            print(f'FILE {i} of {n_files}:')
            print('Retrieving information...')
            dt_vec = c3d_file.stat().st_mtime 
            time_stopped = datetime.datetime.fromtimestamp(dt_vec).strftime('%d-%b-%Y %H:%M:%S.%f')
            print(f'-Recording stopped at {time_stopped}')
        
            # Time that the recording lasts
            duration_s = sec[-1]
            print(f'-Recording duration is {duration_s} seconds')

            # Time at which the recording started
            time_started = (datetime.datetime.strptime(time_stopped, '%d-%b-%Y %H:%M:%S.%f') - datetime.timedelta(seconds=duration_s)).strftime('%d-%b-%Y %H:%M:%S.%f')
            print(f'-Recording started at {time_started}')

            # Sample frequency determination
            tf = sec[1]
            ti = sec[0]
            T = tf - ti
            fs = 1 / T
            print(f'-Sample frequency is {fs} Hz')

            print("Generating time-stamps for file...")

            data.index = pd.date_range(start=time_started, periods=len(sec), freq=pd.DateOffset(seconds=T)).strftime('%d-%b-%Y %H:%M:%S.%f')
            data.index.name = 'Time'
            
            #path_save = f'{file_no_extension}_TimeTable.rda'
            #pyreadr.write_rdata(path_save, {'data_with_timestamps': data_with_timestamps})
            outpath = f"{temp_path}{patient}"
            outfile = os.path.join(outpath, file_name)
            outfile_no_ext = os.path.splitext(outfile)[0]
            csv_file = pathlib.Path(f'{outfile_no_ext}_TimeStamps.csv')
            data.to_csv(csv_file)
            print("Success!")

    print("-------------------------------------")
    print("            PROCESS ENDED            ")
    print("-------------------------------------")

    end_timer = timer()
    elapsed = end_timer - start_timer
    print(f'Code executed in {elapsed:.2f} seconds')
    return data

data_with_timestamps = TSG(302, 20240525, 'D', 9, 9, 9, 'perm')
print("Data with time-stamps:")
print(data_with_timestamps.head(5))
print(data_with_timestamps.tail(5))
