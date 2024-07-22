import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.fftpack import fft
import numpy as np

def plotEMG(data, muscles, y_axis_max, colorsch, title):
    """
    Plots the specified EMG channels

    Args:
    -----------------------------------------------------------------
    -data: dataframe containing the emg data and timestamps (as indexes) to plot
    -muscles: list of ones and/or zeros (1 for yes, 0 for no) of selected channels to plot, or str 'all' to select all channels
    -y_axis_max: int, y-axis limit as absolute value
    -colorsch: whether to plot channels with the same color scheme used in Cometa (1 for yes, 0 for no)
    -title: str, title of the figure

    Returns:
    -----------------------------------------------------------------
    None

    """

    if muscles == 'all':
        muscles = [1] * 8    

    # Get muscles to drop and colors to use
    musc2drop = [index for index, value in enumerate(muscles) if value == 0]
    if colorsch == 1:
        colors = ['firebrick', 'darkorange', 'goldenrod', 'seagreen', 'lightseagreen', 'mediumblue', 'darkorchid', 'sienna']
        colors2plot = [color for index, color in enumerate(colors) if index not in musc2drop]
    elif colorsch == 0:
        colors2plot = ['tab:blue'] * len(data.columns)

    # Get column names of muscles to drop
    cols2drop = data.columns[musc2drop]

    # Drop those channels
    data = data.drop(columns=cols2drop)

    y_axis_min = -1 * y_axis_max
    
    fig, axes = plt.subplots(len(data.columns), sharex=True, figsize=(15, len(data.columns)))

    if len(data.columns) == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.plot(data.index, data.iloc[:, i], colors2plot[i])
        ax.set_ylabel(data.columns[i], rotation=0, labelpad=50)
        ax.set_ylim([y_axis_min, y_axis_max])
        ax.set_xlim([data.index[0], data.index[-1]])

        if i == 0:
            ax.set_title(title, fontsize=14)

        if i == len(data.columns) - 1:
            ax.set_xlabel("Time")
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(interval_multiples=True))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y %H:%M:%S'))
        else:
            ax.set_xticks([])

    plt.tight_layout()
    plt.show()
    plt.savefig(f"{title}.png")

    return None

def plotFreq(signal, channel_name, save_name, fs=1000):
    """
    Plots the frequency spectrum of a single EMG channel

    Args:
    -----------------------------------------------------------------
    -signal: array containing the emg data of a single EMG channel
    -channel_name: str, name of the channel that will be displayed in the title of the figure
    -save_name: str, file name to save the figure as (.png)
    -fs: sampling frequency of the signal, default: 1000 Hz

    Returns:
    -----------------------------------------------------------------
    None

    """
    # Compute period
    T = 1/fs

    # Compute frequency axis
    nsig = len(signal)
    freqs = np.fft.fftfreq(nsig, T)
    freq_axis = freqs[:nsig // 2]
    
    # Apply Fast Fourier Transform
    signalFFT = fft(signal)
    y = (np.abs(signalFFT)[:nsig // 2]) / nsig

    # Plot frequency spectrum
    plt.figure(figsize=(12, 6))
    plt.plot(freq_axis, y)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title(f"Frequency Spectrum of {channel_name}")
    plt.grid()
    plt.tight_layout()
    plt.show()
    plt.savefig(f"{save_name}.png")

    return None
