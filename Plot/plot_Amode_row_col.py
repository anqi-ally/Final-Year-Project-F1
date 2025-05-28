import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from typing import List, Optional

def plot_scan_data(scan_folder: str, selected_files: Optional[List[str]] = None):
    """
    Plot scan data from a selected CSV file.

    Parameters:
    - scan_folder: str, path to the folder containing scan data.
    - selected_files: list[str], must be a list with a single CSV filename (e.g., 'row_2_col_1.csv').
    """
    if selected_files is None or len(selected_files) != 1:
        print("❌ Please provide exactly one CSV filename in the selected_files parameter.")
        return

    filename = selected_files[0]
    match = re.findall(r"\d+", filename)
    if len(match) != 2:
        print(f"❌ Filename does not match 'row_X_col_Y' format: {filename}")
        return

    row_idx = int(match[0])
    col_idx = int(match[1])

    file_path = os.path.join(scan_folder, filename)
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    df = pd.read_csv(file_path)

    # Single plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["Time (s)"], df["Amplitude (V)"], lw=1)
    ax.set_title(f"Row {row_idx}, Col {col_idx}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (V)")
    ax.grid(True)

    plt.suptitle(f"Scan Result: {scan_folder}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# Example
plot_scan_data("data/scan_009", selected_files=[
    "row_29_col_23.csv",
])
