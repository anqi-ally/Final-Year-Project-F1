import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert

# Load numeric signal from a CSV file (automatically skip non-numeric columns)
def load_numeric_signal(filepath):
    df = pd.read_csv(filepath)
    numeric_cols = df.select_dtypes(include=[np.number])
    if numeric_cols.shape[1] == 0:
        numeric_cols = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
    return numeric_cols.iloc[:, 1].dropna().values 

# Parse row and col indices from filename (e.g., row_3_col_4 → (3, 4))
def parse_row_col(filename):
    match = re.search(r'row_(\d+)_col_(\d+)', filename)
    return int(match.group(1)), int(match.group(2)) if match else (None, None)

# Build energy matrix where each element is the integrated envelope value of the corresponding waveform
def build_energy_matrix(folder_path):
    energy_values = {}  # Store energy value for each (row, col) position
    max_row, max_col = 0, 0  # Determine matrix size

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))

            # Required statistics
            envelope = np.abs(hilbert(signal)) 
            rms = np.sqrt(np.mean(signal**2))
            envelope_sum = np.sum(envelope)
            envelope_max = np.max(envelope)
            signal_variance = np.var(signal)
            energy = np.sum(envelope)  

            energy_values[(row, col)] = rms
            max_row = max(max_row, row)
            max_col = max(max_col, col)

    # Initialize matrix based on max row/col
    matrix = np.zeros((max_row, max_col))
    for (row, col), energy in energy_values.items():
        matrix[row - 1, col - 1] = energy

    return matrix

def build_max_envelope_matrix(folder_path):
    values = {}
    max_row, max_col = 0, 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))
            envelope = np.abs(hilbert(signal))
            envelope_max = np.max(envelope)

            values[(row, col)] = envelope_max
            max_row = max(max_row, row)
            max_col = max(max_col, col)

    matrix = np.zeros((max_row, max_col))
    for (row, col), val in values.items():
        matrix[row - 1, col - 1] = val
    return matrix

def build_sum_envelope_matrix(folder_path):
    values = {}
    max_row, max_col = 0, 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))
            envelope = np.abs(hilbert(signal))
            envelope_sum = np.sum(envelope) 

            values[(row, col)] = envelope_sum
            max_row = max(max_row, row)
            max_col = max(max_col, col)

    matrix = np.zeros((max_row, max_col))
    for (row, col), val in values.items():
        matrix[row - 1, col - 1] = val
    return matrix

# Automatically round min/max to nearest tens for consistent grayscale mapping
def auto_round_limits(matrix):
    raw_min = matrix.min()
    raw_max = matrix.max()
    return np.floor(raw_min / 10) * 10, np.ceil(raw_max / 10) * 10

# Normalize energy matrix to 0–255 grayscale integers
def normalize_to_grayscale(matrix, min_val, max_val):
    norm = (matrix - min_val) / (max_val - min_val)  # Linear normalization
    norm = np.clip(norm, 0, 1)  # Clip to [0, 1]
    return np.round(norm * 255).astype(int)  # Map to grayscale integers

# Plot B-mode image (grayscale), optionally save to file
def plot_bmode(grayscale_matrix, min_val, max_val, save_path=None, show_labels=True, title="B-mode Image"):
    fig, ax = plt.subplots(figsize=(6, 6))
    cax = ax.imshow(grayscale_matrix, cmap='gray', origin='upper')  # Show grayscale image
    fig.colorbar(cax, label=f'Grayscale (Mapped {int(min_val)}–{int(max_val)})')  # Colorbar
    ax.set_title(title)
    ax.set_xlabel("Scan Column")
    ax.set_ylabel("Scan Row")
    ax.set_xticks(np.arange(grayscale_matrix.shape[1]))
    ax.set_yticks(np.arange(grayscale_matrix.shape[0]))

    # Show grayscale values on each pixel (optional)
    if show_labels:
        for i in range(grayscale_matrix.shape[0]):
            for j in range(grayscale_matrix.shape[1]):
                ax.text(j, i, f"{grayscale_matrix[i, j]}", va='center', ha='center', color='red', fontsize=10)

    plt.tight_layout()
    # Uncomment to save image
    # if save_path:
    #     plt.savefig(save_path, dpi=300)
    plt.show()

def generate_bmode_from_folder(folder_path, scan_name="unknown", save_path=None):
    energy_matrix = build_energy_matrix(folder_path)
    min_val, max_val = auto_round_limits(energy_matrix)
    grayscale_matrix = normalize_to_grayscale(energy_matrix, min_val, max_val)
    plot_bmode(grayscale_matrix, min_val, max_val, save_path=save_path,
               title=f"B-mode Image (RMS Energy) - {scan_name}")

    # Image based on envelope max
    max_env_matrix = build_max_envelope_matrix(folder_path)
    min_env, max_env = auto_round_limits(max_env_matrix)
    grayscale_env = normalize_to_grayscale(max_env_matrix, min_env, max_env)
    plot_bmode(grayscale_env, min_env, max_env, save_path=None, show_labels=False,
               title=f"B-mode Image (Envelope Max) - {scan_name}")
    
    # Image based on envelope sum
    sum_env_matrix = build_sum_envelope_matrix(folder_path)
    min_sum, max_sum = auto_round_limits(sum_env_matrix)
    grayscale_sum = normalize_to_grayscale(sum_env_matrix, min_sum, max_sum)
    plot_bmode(grayscale_sum, min_sum, max_sum, save_path=None, show_labels=False,
               title=f"B-mode Image (Envelope Sum) - {scan_name}")

# Automatically process all scan_xxx/filtered folders in base_path
def process_all_scans(base_path="data", start_index=4, show_labels=True):
    scan_folders = sorted([f for f in os.listdir(base_path) if f.startswith("scan_")])

    for scan_name in scan_folders:
        try:
            scan_number = int(scan_name.split("_")[1])
        except (IndexError, ValueError):
            print(f"[Skipped] {scan_name}: Failed to parse scan number")
            continue

        if scan_number < start_index:
            continue

        scan_dir = os.path.join(base_path, scan_name)
        filtered_path = os.path.join(scan_dir, "filtered")

        if not os.path.isdir(filtered_path):
            print(f"[Skipped] {scan_name}: 'filtered' folder not found")
            continue

        csv_files = [f for f in os.listdir(filtered_path) if f.endswith(".csv")]
        if not csv_files:
            print(f"[Skipped] {scan_name}: No .csv files in filtered directory")
            continue

        print(f"[Processing] {scan_name}/filtered/")
        save_path = os.path.join(scan_dir, f"bmode_{scan_name}.png")
        generate_bmode_from_folder(filtered_path, scan_name=scan_name, save_path=save_path)

# Example usage
# from b_mode import process_all_scans
process_all_scans(base_path="data", start_index=9)
