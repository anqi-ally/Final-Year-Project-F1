import pandas as pd
import numpy as np
import os
import re

# 设置目标扫描文件夹路径
scan_folder = "data/scan_008"
output_folder = os.path.join(scan_folder, "filtered")
os.makedirs(output_folder, exist_ok=True)

# 获取所有符合 row_x_col_y.csv 命名的文件
file_list = [f for f in os.listdir(scan_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]

def extract_waveform_within_window(df, start_threshold=0.00058, duration=25e-6):
    """
    提取满足起始时间阈值之后，固定持续时间窗口内的波形数据。

    参数:
    - df: 包含 Time 和 Amplitude 的 DataFrame
    - start_threshold: 起始时间阈值（单位：秒），小于该值的时间将被裁掉
    - duration: 持续时间窗口（单位：秒），从起始点开始往后截取的时间长度

    返回:
    - 新的 DataFrame，只包含裁剪后的时间与振幅
    """
    time = df["Time (s)"].astype(float).values
    amp = df["Amplitude (V)"].astype(float).values

    # 找到大于起始阈值的第一个索引
    valid_indices = np.where(time > start_threshold)[0]
    if len(valid_indices) == 0:
        return pd.DataFrame(columns=["Time (s)", "Amplitude (V)"])

    start_idx = valid_indices[0]
    t0 = time[start_idx]
    end_time = t0 + duration

    # 获取在这个时间窗口内的所有数据
    window_mask = (time >= t0) & (time <= end_time)
    time_final = time[window_mask] - t0  # 时间归零
    amp_final = amp[window_mask]

    return pd.DataFrame({
        "Time (s)": time_final,
        "Amplitude (V)": amp_final
    })

# 处理并保存每个文件
for f in file_list:
    file_path = os.path.join(scan_folder, f)
    df = pd.read_csv(file_path, skiprows=1)
    df.columns = ["Time (s)", "Amplitude (V)"]
    filtered_df = extract_waveform_within_window(df, start_threshold=0.00026, duration=25e-6)
    filtered_df.to_csv(os.path.join(output_folder, f), index=False)
