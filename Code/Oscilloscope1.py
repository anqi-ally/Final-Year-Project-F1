import os
import pyvisa
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from const import data_dir
from Signal_function import Burst_generate
from Setup import OSC_ADDRESS, SIGNAL_PARAMS

# 创建扫描数据的存储文件夹
def create_scan_folder():
    os.makedirs(data_dir, exist_ok=True)
    existing_scans = [d for d in os.listdir(data_dir) if d.startswith('scan_') and os.path.isdir(os.path.join(data_dir, d))]
    scan_numbers = [int(d.split('_')[1]) for d in existing_scans if d.split('_')[1].isdigit()]
    next_scan_num = max(scan_numbers, default=0) + 1
    scan_folder = os.path.join(data_dir, f'scan_{next_scan_num:03d}')
    os.makedirs(scan_folder)
    return scan_folder

# ✅ 新函数：配置示波器采集设置
def configure_oscilloscope_for_burst(osc, SIGNAL_PARAMS):
    """
    Configure oscilloscope acquisition settings for burst waveform capture.
    """
    def vbs(osc, cmd):
        osc.write(f"VBS '{cmd}'")
        time.sleep(0.1)

    freq = SIGNAL_PARAMS["frequency"]
    amp = SIGNAL_PARAMS["amplitude"]

    # 设置示波器时间轴为显示 5 个周期（每个周期 = 1/freq）
    n_cycles_to_display = 5
    hor_scale = (n_cycles_to_display / freq) / 10  # 显示 10 格，1格显示 1/10
    ver_scale = amp / 4                             # 让信号高度占据约 80%
    sampling_rate = freq * 100                       # 至少 20x 频率采样

    # 下发到示波器
    vbs(osc, f"app.Acquisition.Horizontal.HorScale = {hor_scale}")
    vbs(osc, f"app.Acquisition.C1.VerScale = {ver_scale}")
    vbs(osc, f"app.Acquisition.Horizontal.SampleRate = {sampling_rate}")
    vbs(osc, "app.Acquisition.C1.Offset = 0")
    vbs(osc, "app.Acquisition.C1.View = true")
    vbs(osc, "app.Acquisition.Trigger.Source = \"C1\"")
    vbs(osc, "TRIG_MODE AUTO")  # 对连续信号建议使用 AUTO 触发模式

# ✅ 主函数：读取波形并保存
def read_oscilloscope_and_save(osc, cross, s, scan_folder):
    try:
        configure_oscilloscope_for_burst(osc, SIGNAL_PARAMS)

        osc.write("C1:WF? DAT1")
        raw_data = osc.query_binary_values("C1:WF? DAT1", datatype="B", container=np.array)

        scale = float(osc.query("C1:VDIV?").strip().split(" ")[1])
        v_offset = float(osc.query("C1:OFST?").strip().split(" ")[1])
        scale1 = 1/30
        voltages = ((raw_data - 128) * scale + v_offset - 128) * scale1

        # time_div = float(osc.query("TDIV?").strip().split(" ")[1])
        # num_points = len(raw_data)
        # time_values = np.linspace(0, num_points * time_div / 1, num_points)

        # # 输入振幅
        # amp_pp= SIGNAL_PARAMS["amplitude"]

        # # 找到波形的最大最小值
        # sel_data = (raw_data - 128)
        # min_val = sel_data.min()
        # max_val = sel_data.max()

        # # 动态缩放到 
        # voltages = (sel_data - (max_val + min_val)/2) / (max_val - min_val) * amp_pp

        # sampling_rate = SIGNAL_PARAMS["frequency"] * 100
        # sampling_interval = 1 / sampling_rate
        # time_values = np.arange(len(raw_data)) * sampling_interval

        time_div = float(osc.query("TDIV?").strip().split(" ")[1])
        num_points = len(raw_data)
        time_span = 10 * time_div  # 总时间范围（10格）
        # dt = time_span / num_points  # 每个点的时间间隔
        time_values = np.linspace(0, time_span, num_points, endpoint=False)


        filename = f"row_{cross+1}_col_{s}.csv"
        file_path = os.path.join(scan_folder, filename)
        df = pd.DataFrame({"Time (s)": time_values, "Amplitude (V)": voltages})
        df.to_csv(file_path, index=False)
        print(f"✅ Data saved to: {file_path}")

        # 保存波形设置参数为 CSV
        param_path = os.path.join(scan_folder, "wave_parameter.csv")
        param_df = pd.DataFrame(list(SIGNAL_PARAMS.items()), columns=["Parameter", "Value"])
        param_df.to_csv(param_path, index=False)
        print(f"📝 Signal parameters saved to: {param_path}")


    except Exception as e:
        print(f"❌ Failed to read oscilloscope data: {e}")


# ✅ 发射脉冲并调用读取函数
def send_burst(sg, cross, s, scan_folder):
    Burst_generate(
        sg,
        shape="SIN",
        frequency=100,
        amplitude=1,
        burst_ncycles=60,
    )
    print("trigger_count")
    time.sleep(1)
    read_oscilloscope_and_save(cross, s, scan_folder)
    time.sleep(0.5)
    print(f"📡 Captured triggered data for row {cross+1}, column {s}...")
