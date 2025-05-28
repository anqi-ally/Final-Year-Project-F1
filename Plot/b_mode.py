import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert

def load_numeric_signal(filepath):
    df = pd.read_csv(filepath)
    numeric_cols = df.select_dtypes(include=[np.number])
    if numeric_cols.shape[1] == 0:
        numeric_cols = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
    return numeric_cols.iloc[:, 1].dropna().values

def parse_row_col(filename):
    match = re.search(r'row_(\d+)_col_(\d+)', filename)
    return int(match.group(1)), int(match.group(2)) if match else (None, None)

def get_depth_axis(filepath, sound_speed=1480):
    df = pd.read_csv(filepath)
    if df.shape[1] < 1:
        raise ValueError("Missing time column in CSV")
    time_array = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().values
    depth_mm = (time_array * sound_speed / 2) * 1000
    return depth_mm

def build_envelope_volume(folder_path):
    max_row, max_col = 0, 0
    waveform_length = None

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))
            if waveform_length is None and len(signal) > 0:
                waveform_length = len(signal)
            max_row = max(max_row, row)
            max_col = max(max_col, col)

    if waveform_length is None:
        raise ValueError("No valid waveform length detected.")

    envelope_volume = np.zeros((max_row, max_col, waveform_length))

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))
            if len(signal) == 0:
                envelope = np.zeros(waveform_length)
            else:
                envelope = np.abs(hilbert(signal))
                if len(envelope) < waveform_length:
                    padded = np.zeros(waveform_length)
                    padded[:len(envelope)] = envelope
                    envelope = padded
            envelope_volume[row - 1, col - 1, :] = envelope

    return envelope_volume

def read_scan_params(setup_path="Code/Setup.py"):
    scan_params = {}
    with open(setup_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    inside_params = False
    for line in lines:
        line = line.strip()
        if line.startswith("SCAN_PARAMS"):
            inside_params = True
            continue
        if inside_params:
            if line.startswith("}"):
                break
            match = re.match(r'"([^\"]+)"\s*:\s*"?(.*?)"?,?', line)
            if match:
                key, value = match.groups()
                try:
                    scan_params[key] = float(value)
                except ValueError:
                    scan_params[key] = value
    return scan_params

def plot_single_cross_section(envelope_volume, depth_axis, row_index=None, col_index=None):
    if row_index is not None:
        data = envelope_volume[row_index - 1, :, :]
        y_label = f"Col index @ row {row_index}"
        title = f"B-mode row cut @ row {row_index}"
    elif col_index is not None:
        data = envelope_volume[:, col_index - 1, :]
        y_label = f"Row index @ col {col_index}"
        title = f"B-mode col cut @ col {col_index}"
    else:
        raise ValueError("Either row_index or col_index must be specified")

    max_val = np.max(data)
    eps = max_val / (10**(40 / 20))
    log_data = 20 * np.log10(data / (eps + 1e-12))

    if depth_axis is not None and len(depth_axis) != data.shape[1]:
        depth_axis = np.linspace(depth_axis[0], depth_axis[-1], data.shape[1])

    extent = [depth_axis[0], depth_axis[-1], 0, data.shape[0]]
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(log_data, cmap='gray', aspect='auto', origin='upper', extent=extent)
    ax.set_xlabel("Depth (mm)")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    fig.colorbar(cax, label="Envelope Amplitude (dB)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    base_path = "data"
    setup_path = "Code/Setup.py"
    scan_folders = [f for f in os.listdir(base_path) if f.startswith("scan_")]

    if not scan_folders:
        print("No scan_xxx folders found")
        exit()

    print("Available scan folders:")
    for i, folder in enumerate(scan_folders):
        print(f"{i + 1}. {folder}")

    selection = input("Enter the index of the scan folder to process (e.g., 1 for the first scan_xxx): ").strip()
    try:
        selected_index = int(selection) - 1
        scan_name = scan_folders[selected_index]
    except (ValueError, IndexError):
        print("Invalid input. Program exiting.")
        exit()

    scan_dir = os.path.join(base_path, scan_name)
    filtered_path = os.path.join(scan_dir, "filtered")

    if not os.path.isdir(filtered_path):
        print(f"[Error] No 'filtered' folder in {scan_name}")
    else:
        csv_files = [f for f in os.listdir(filtered_path) if f.endswith(".csv")]
        if not csv_files:
            print(f"[Error] No .csv files in {scan_name}/filtered/")
        else:
            print(f"[Processing] {scan_name}/filtered/")
            scan_params = read_scan_params(setup_path)
            scan_axis = scan_params.get("scan_axis", "Z")
            cross_axis = scan_params.get("cross_axis", "Y")
            envelope_volume = build_envelope_volume(scan_dir)
            depth_axis = get_depth_axis(os.path.join(filtered_path, csv_files[0]))

            # 👉 Modify here to choose which row or column to display
            plot_single_cross_section(envelope_volume, depth_axis, col_index=13)
            # plot_single_cross_section(envelope_volume, depth_axis, row_index=1)
