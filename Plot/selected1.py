import pandas as pd
import numpy as np
import os
import re

# 设置目标扫描文件夹路径
scan_folder = "data/scan_0011"
output_folder = os.path.join(scan_folder, "filtered")
os.makedirs(output_folder, exist_ok=True)

# 获取所有符合 row_x_col_y.csv 命名的文件
file_list = [f for f in os.listdir(scan_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]

def extract_non_flat_waveform(df, time_threshold=0.00026):
    time = df["Time (s)"].astype(float).values
    amp = df["Amplitude (V)"].astype(float).values

    # 保留 time > 0.00026 的数据
    valid_indices = np.where(time > time_threshold)[0]
    if len(valid_indices) == 0:
        return pd.DataFrame(columns=["Time (s)", "Amplitude (V)"])  # 无满足条件的数据

    cut_start = valid_indices[0]
    time_final = time[cut_start:] - time[cut_start]  # 将时间重新归零
    amp_final = amp[cut_start:]

    return pd.DataFrame({
        "Time (s)": time_final,
        "Amplitude (V)": amp_final
    })





# 处理并保存
for f in file_list:
    file_path = os.path.join(scan_folder, f)
    df = pd.read_csv(file_path, skiprows=1)
    df.columns = ["Time (s)", "Amplitude (V)"]
    filtered_df = extract_non_flat_waveform(df)
    filtered_df.to_csv(os.path.join(output_folder, f), index=False)
