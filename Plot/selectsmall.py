import pandas as pd
import numpy as np
import os
import re

# Set the target scan folder path
scan_folder = "data/scan_008"
output_folder = os.path.join(scan_folder, "filtered")
os.makedirs(output_folder, exist_ok=True)

# Get all files matching the pattern row_x_col_y.csv
file_list = [f for f in os.listdir(scan_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]

def extract_waveform_within_window(df, start_threshold=0.00058, duration=25e-6):
    """
    Extract waveform data within a fixed time window starting after a threshold.

    Parameters:
    - df: DataFrame containing Time and Amplitude columns
    - start_threshold: Starting time threshold (in seconds); data before this will be excluded
    - duration: Duration of the time window (in seconds) to extract from the threshold point

    Returns:
    - A new DataFrame containing time-zeroed waveform data within the specified window
    """
    time = df["Time (s)"].astype(float).values
    amp = df["Amplitude (V)"].astype(float).values

    # Find the first index where time exceeds the threshold
    valid_indices = np.where(time > start_threshold)[0]
    if len(valid_indices) == 0:
        return pd.DataFrame(columns=["Time (s)", "Amplitude (V)"])

    start_idx = valid_indices[0]
    t0 = time[start_idx]
    end_time = t0 + duration

    # Mask to select data within the window
    window_mask = (time >= t0) & (time <= end_time)
    time_final = time[window_mask] - t0  # Zero the time axis
    amp_final = amp[window_mask]

    return pd.DataFrame({
        "Time (s)": time_final,
        "Amplitude (V)": amp_final
    })

# Process and save each file
for f in file_list:
    file_path = os.path.join(scan_folder, f)
    df = pd.read_csv(file_path, skiprows=1)
    df.columns = ["Time (s)", "Amplitude (V)"]
    filtered_df = extract_waveform_within_window(df, start_threshold=0.00026, duration=25e-6)
    filtered_df.to_csv(os.path.join(output_folder, f), index=False)
