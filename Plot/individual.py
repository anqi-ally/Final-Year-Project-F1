import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from typing import List, Optional

def plot_scan_data(scan_folder: str, selected_files: Optional[List[str]] = None):
    """
    绘制扫描数据波形图（仅支持绘制一个文件）。
    
    参数:
    - scan_folder: str，扫描数据所在的文件夹路径。
    - selected_files: list[str]，必须是长度为1的列表，指定绘制的 CSV 文件名（如 'row_2_col_1.csv'）。
    """
    if selected_files is None or len(selected_files) != 1:
        print("❌ 请仅提供一个 CSV 文件名作为 selected_files 参数。")
        return

    filename = selected_files[0]
    match = re.findall(r"\d+", filename)
    if len(match) != 2:
        print(f"❌ 文件名不符合 row_X_col_Y 格式：{filename}")
        return

    row_idx = int(match[0])
    col_idx = int(match[1])

    file_path = os.path.join(scan_folder, filename)
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    df = pd.read_csv(file_path)

    # 单张图
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(df["Time (s)"], df["Amplitude (V)"], lw=1)
    ax.set_title(f"Row {row_idx}, Col {col_idx}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (V)")
    ax.grid(True)

    plt.suptitle(f"Scan Result: {scan_folder}", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# ✅ 示例：只绘制 row_2_col_1.csv
plot_scan_data("data/scan_009", selected_files=[
    "row_29_col_23.csv",
])
