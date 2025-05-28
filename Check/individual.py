import pandas as pd                  # 导入 pandas 库，用于数据读取和处理
import matplotlib.pyplot as plt      # 导入 matplotlib 的 pyplot 模块用于绘图
import os                            # 导入 os 模块，用于文件和路径操作
import re                            # 导入正则表达式模块，用于筛选文件名

# 设置目标扫描文件夹路径
scan_folder = "data/scan_001"        # 指定存放扫描数据文件的目录

# 获取所有符合 row_x_col_y.csv 命名的文件
file_list = [f for f in os.listdir(scan_folder) if re.match(r"row_\d+_col_\d+\.csv", f)]
# 遍历文件夹中所有文件，筛选出符合 row_数字_col_数字.csv 格式的文件名

# 提取最大行列数用于子图排布
positions = [re.findall(r"\d+", f) for f in file_list]
# 从每个文件名中提取出 row 和 col 的数字
rows = max(int(p[0]) for p in positions)
cols = max(int(p[1]) for p in positions)
# 获取最大的行列编号，以确定整个图像的子图排布

fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows), sharex=True, sharey=True)
# 创建一个 rows 行、cols 列的子图网格，共享坐标轴，并根据图像数量设置整体图像尺寸

for f in file_list:
    match = re.findall(r"\d+", f)
    row_idx = int(match[0]) - 1       # 文件中的 row 编号从 1 开始，需要减 1 转为索引
    col_idx = int(match[1]) - 1       # 同上，列编号也需要减 1
    file_path = os.path.join(scan_folder, f)  # 构造该 CSV 文件的完整路径

    df = pd.read_csv(file_path)       # 读取 CSV 文件为 DataFrame
    ax = axes[row_idx, col_idx] if rows > 1 and cols > 1 else (
        axes[col_idx] if rows == 1 else axes[row_idx]
    )
    # 根据行列数选择正确的子图对象，如果只有一行或一列则要特殊处理 axes 索引结构

    ax.plot(df["Time (s)"], df["Amplitude (V)"], lw=1)  # 绘制电压随时间变化曲线
    ax.set_title(f"Row {row_idx+1}, Col {col_idx+1}")   # 设置子图标题，回归到从1开始的编号
    ax.grid(True)                                       # 添加网格以增强可读性

# 添加全局 x 和 y 标签
fig.text(0.5, 0.04, 'Time (s)', ha='center', fontsize=12)  # 设置整幅图的横轴标签
fig.text(0.04, 0.5, 'Amplitude (V)', va='center', rotation='vertical', fontsize=12)
# 设置整幅图的纵轴标签

plt.suptitle(f"Scan Result: {scan_folder}", fontsize=16)   # 设置整个图像的总标题
# plt.tight_layout()
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])  # 调整子图间距，避免标题和标签被遮挡
plt.show()  # 显示图像
