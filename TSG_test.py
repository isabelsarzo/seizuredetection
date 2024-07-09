import os
import pandas as pd
import datetime
import pathlib

def TSG(patient, date, shift, batch, n_files, start_idx, folder):
    print("-------------------------------------")
    print("           PROCESS STARTED           ")
    print("-------------------------------------")

    patient = str(patient)
    date = str(date)
    batch = str(batch)

    file = pathlib.Path(r'i:\Chercheurs\BouAssi_Elie\TeamMembers\SarzoWabi_Isabel\Cometa Project\Pruebas\Prueba_1_1.txt')
    data = pd.read_csv(file, sep='\t', skiprows=[0], engine='python')
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
        print('Retrieving file information...')
        dt_vec = c3d_file.stat().st_mtime 
        time_stopped = datetime.datetime.fromtimestamp(dt_vec).strftime('%d-%b-%Y %H:%M:%S.%f')
        print(f'Recording stopped at {time_stopped}')
    
        # Time that the recording lasts
        duration_s = sec[-1]
        print(f'Recording duration is {duration_s} seconds')

        # Time at which the recording started
        time_started = datetime.datetime.strptime(time_stopped, '%d-%b-%Y %H:%M:%S.%f') - datetime.timedelta(seconds=duration_s)
        print(f'Recording started at {time_started}')

        # Sample frequency determination
        tf = sec[1]
        ti = sec[0]
        T = tf - ti
        fs = 1 / T
        print(f'Sample frequency is {fs} Hz')

        print("Generating time-stamps for file...")

        tt = pd.DataFrame({'sec': sec})
        tt.index = pd.date_range(start=time_started, periods=len(tt), freq=pd.DateOffset(seconds=T))
        tt.index.name = 'Time'
        data_with_timestamps = tt.join()
        data_with_timestamps = pd.merge(tt, data, left_index=True, right_on='sec')
        
        #path_save = f'{file_no_extension}_TimeTable.rda'
        #pyreadr.write_rdata(path_save, {'data_with_timestamps': data_with_timestamps})

        print("Success")

    print("-------------------------------------")
    print("            PROCESS ENDED            ")
    print("-------------------------------------")

    return data_with_timestamps

data_with_timestamps = TSG(308, 20240703, 'D', 43, 8, 1, 'perm')
print(data_with_timestamps.head(10))