import pandas as pd
import datetime

def generate_timestamps(c3d_filepath, time):
    # TODO: write docstring
    print("Retrieving recording information...")

    # Get period
    T = time[1] - time[0]

    # Get duration
    dur = (len(time) - 1) * T

    # Get the last modification date-time of the c3d file
    dt_mod = c3d_filepath.stat().st_mtime 
    time_stopped = datetime.datetime.fromtimestamp(dt_mod).strftime('%d-%b-%Y %H:%M:%S.%f')

    # Calculate the time at which the recording started
    time_started = (datetime.datetime.strptime(time_stopped, '%d-%b-%Y %H:%M:%S.%f') - datetime.timedelta(seconds=dur)).strftime('%d-%b-%Y %H:%M:%S.%f')
    
    print(f'-Recording started at {time_started}')
    print(f'-Recording stopped at {time_stopped}')
    print(f'-Recording duration is {dur} seconds')
    print(f'-Sample frequency is {1/T} Hz')

    # Generate time-stamp for each datapoint
    print("Generating time-stamps...")
    timestamps = pd.date_range(start=time_started, periods=len(time), freq=pd.DateOffset(seconds=T)).strftime('%d-%b-%Y %H:%M:%S.%f')
    print("Success!")

    return timestamps

