import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert

# 读取 CSV 文件中的波形数据（返回数值列）
def load_numeric_signal(filepath):
    df = pd.read_csv(filepath)
    numeric_cols = df.select_dtypes(include=[np.number])  # 选择数值列
    if numeric_cols.shape[1] == 0:
        # 如果没有明确的数值列，尝试强制转换
        numeric_cols = df.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
    return numeric_cols.iloc[:, 1].dropna().values  # 返回第一列有效数值数据


# 从文件名中提取 row 和 col 信息
def parse_row_col(filename):
    match = re.search(r'row_(\d+)_col_(\d+)', filename)
    return int(match.group(1)), int(match.group(2)) if match else (None, None)

# 构建 3D envelope_map，shape = (max_row, max_col, waveform_length)
def build_envelope_volume(folder_path):
    envelope_dict = {}
    max_row, max_col = 0, 0
    waveform_length = None

    # 第一遍确定所有位置和最长波形长度
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))

            if waveform_length is None and len(signal) > 0:
                waveform_length = len(signal)

            max_row = max(max_row, row)
            max_col = max(max_col, col)

    if waveform_length is None:
        raise ValueError("未能识别任何有效的波形长度。")

    # 初始化全 0 体积
    envelope_volume = np.zeros((max_row, max_col, waveform_length))

    # 第二遍真正填入包络
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and 'row_' in filename and 'col_' in filename:
            row, col = parse_row_col(filename)
            signal = load_numeric_signal(os.path.join(folder_path, filename))

            if len(signal) == 0:
                envelope = np.zeros(waveform_length)
            else:
                envelope = np.abs(hilbert(signal))
                # 若长度不足则右侧补 0
                if len(envelope) < waveform_length:
                    padded = np.zeros(waveform_length)
                    padded[:len(envelope)] = envelope
                    envelope = padded

            envelope_volume[row - 1, col - 1, :] = envelope

    return envelope_volume

def plot_bmode_full_image(envelope_volume, db_range=40, title="Full B-mode", save_path=None):
    Ny, Nz, Nx = envelope_volume.shape
    combined = envelope_volume.reshape(Ny * Nz, Nx)

    # log 压缩
    max_val = np.max(combined)
    eps = max_val / (10**(db_range / 20))
    log_data = 20 * np.log10(combined / (eps + 1e-12))

    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.imshow(log_data, cmap='gray', aspect='auto', origin='upper')
    ax.set_title(title)
    ax.set_xlabel("Time / Depth Index")
    ax.set_ylabel("Scan Position Index (row × col)")
    fig.colorbar(cax, label="Envelope Amplitude (dB)")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()


# 绘制某一 col（z方向）上的 slice：Y vs X 包络图
def plot_bmode_slice(envelope_volume, col_index=0, db_range=40, title="B-mode Slice", save_path=None):
    slice_data = envelope_volume[:, col_index, :]  # shape: (Ny, Nx)

    # 对 envelope 做 log 压缩（dB 显示）
    max_val = np.max(slice_data)
    eps = max_val / (10**(db_range / 20))
    log_data = 20 * np.log10(slice_data / (eps + 1e-12))
    
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(log_data, cmap='gray', aspect='auto', origin='upper')
    ax.set_title(f"{title} @ col {col_index}")
    ax.set_xlabel("Time / Depth Index")
    ax.set_ylabel("Row Index")
    fig.colorbar(cax, label='Envelope Amplitude (dB)')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
    plt.show()

# 自动处理 base_path 下所有扫描的 slice 图像
def process_all_slices(base_path="data", start_index=4, slice_index=0):
    scan_folders = [f for f in os.listdir(base_path) if f.startswith("scan_")]

    for scan_name in scan_folders:
        try:
            scan_number = int(scan_name.split("_")[1])
        except (IndexError, ValueError):
            print(f"[跳过] {scan_name}: 无法解析编号")
            continue

        if scan_number < start_index:
            continue

        scan_dir = os.path.join(base_path, scan_name)
        filtered_path = os.path.join(scan_dir, "filtered")

        if not os.path.isdir(filtered_path):
            print(f"[跳过] {scan_name}: 没有 filtered 文件夹")
            continue

        csv_files = [f for f in os.listdir(filtered_path) if f.endswith(".csv")]
        if not csv_files:
            print(f"[跳过] {scan_name}: filtered 目录中无 .csv 文件")
            continue

        print(f"[处理中] {scan_name}/filtered/")
        save_path = os.path.join(scan_dir, f"bmode_{scan_name}.png")
        envelope_volume = build_envelope_volume(scan_dir)
        # plot_bmode_slice(envelope_volume, col_index=slice_index,
        #                  title=f"B-mode Slice - {scan_name}", save_path=None)
        plot_bmode_full_image(envelope_volume,
                      title=f"B-mode Full View - {scan_name}",
                      save_path=save_path)




process_all_slices(base_path="data", start_index=4, slice_index=0)