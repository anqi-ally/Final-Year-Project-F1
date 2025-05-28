import pandas as pd
import numpy as np
import os
import re

# Set target scan folder path
scan_folder = "data/scan_002"
output_folder = os.path.join(scan_folder, "filtered")
os.makedirs(output_folder, exist_ok=True)

# Get all files matching the pattern row_x_col_y.csv
file_list = [f for f in os.listdir(scan_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]

def extract_non_flat_waveform(df, std_window=10, std_thresh=0.03, buffer=10):
    time = df["Time (s)"].astype(float).values
    amp = df["Amplitude (V)"].astype(float).values

    # Calculate moving standard deviation
    rolling_std = pd.Series(amp).rolling(std_window, center=True).std().fillna(0).values

    # Find indices of active regions
    active_indices = np.where(rolling_std > std_thresh)[0]
    if len(active_indices) == 0:
        return pd.DataFrame(columns=["Time (s)", "Amplitude (V)"])  # No valid waveform found

    # Get range around the active region
    start = max(0, active_indices[0] - buffer)
    end = min(len(amp), active_indices[-1] + buffer)

    time_cut = time[start:end]
    amp_cut = amp[start:end]

    # Use the 11th point (index 10) as the new zero time
    if len(time_cut) > 10:
        time_zero = time_cut[10]
    else:
        time_zero = time_cut[0]  # Prevent errors if the segment is too short

    time_aligned = time_cut - time_zero

    return pd.DataFrame({
        "Time (s)": time_aligned,
        "Amplitude (V)": amp_cut
    })

# Process and save
for f in file_list:
    file_path = os.path.join(scan_folder, f)
    df = pd.read_csv(file_path, skiprows=1)
    df.columns = ["Time (s)", "Amplitude (V)"]
    filtered_df = extract_non_flat_waveform(df)
    filtered_df.to_csv(os.path.join(output_folder, f), index=False)
