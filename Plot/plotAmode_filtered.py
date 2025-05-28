import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# Set path to filtered data
filtered_folder = "data/scan_009/filtered"

# Get all files matching the naming pattern row_x_col_y.csv
file_list = [f for f in os.listdir(filtered_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]

# Extract maximum row and column indices for subplot layout
positions = [re.findall(r"\d+", f) for f in file_list]
rows = max(int(p[0]) for p in positions)
cols = max(int(p[1]) for p in positions)

# Create subplots
fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows), sharex=True, sharey=True)

for f in file_list:
    match = re.findall(r"\d+", f)
    row_idx = int(match[0]) - 1
    col_idx = int(match[1]) - 1
    file_path = os.path.join(filtered_folder, f)

    df = pd.read_csv(file_path)
    ax = axes[row_idx, col_idx] if rows > 1 and cols > 1 else (
        axes[col_idx] if rows == 1 else axes[row_idx]
    )
    if not df.empty:
        ax.plot(df["Time (s)"], df["Amplitude (V)"], lw=1)
    ax.set_title(f"Row {row_idx+1}, Col {col_idx+1}")
    ax.grid(True)

plt.suptitle(f"Filtered Scan Result: {filtered_folder}", fontsize=16)
plt.tight_layout()
plt.show()
