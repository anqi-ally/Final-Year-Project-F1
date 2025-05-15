import time
from pymeasure.instruments.agilent import Agilent33500
from pyvisa import ResourceManager
from Setup import SIGNAL_PARAMS, SCAN_PARAMS, HOST, PORT, SG_ADDRESS, OSC_ADDRESS
from Signal_function import Burst_generate, Continuous_generate, Trigger_generate
import numpy as np
import os
from const import data_dir
import pandas as pd

# ✅ Connect to signal generator
sg = Agilent33500(SG_ADDRESS)
print("✅ Signal generator connected:", sg.id)

def configure_oscilloscope_for_burst(osc):
    def vbs(osc, cmd):
        osc.write(f"VBS '{cmd}'")
        time.sleep(0.1)

    freq = SIGNAL_PARAMS["frequency"]
    amp = SIGNAL_PARAMS["amplitude"]
    n_cycles = SIGNAL_PARAMS["burst_ncycles"]

    burst_duration = n_cycles / freq
    hor_scale = burst_duration/5
    ver_scale = amp*2
    Sampling_Rate = freq * 100

    vbs(osc, f"app.Acquisition.Horizontal.HorScale = 50e-6") # 50e-6
    vbs(osc, f"app.Acquisition.C4.VerScale = 0.5")  #0.5
    vbs(osc, f"app.Acquisition.Horizontal.SampleRate = 250e6") #100e6
    vbs(osc, "app.Acquisition.C4.Offset = 0")
    vbs(osc, "app.Acquisition.C4.View = true")
    vbs(osc, "app.Acquisition.Trigger.Source = \"C4\"")
    osc.write("TRIG_MODE Norm")

    #-------------------------------------------------------------------------------

    # freq = SIGNAL_PARAMS["frequency"]
    # amp = SIGNAL_PARAMS["amplitude"]

    # # 设置示波器时间轴为显示 5 个周期（每个周期 = 1/freq）
    # n_cycles_to_display = 5
    # hor_scale = (n_cycles_to_display / freq) / 10  # 显示 10 格，1格显示 1/10
    # ver_scale = amp / 4                             # 让信号高度占据约 80%
    # sampling_rate = freq * 100                       # 至少 20x 频率采样

    # # 下发到示波器
    # vbs(osc, f"app.Acquisition.Horizontal.HorScale = 50e-6")
    # vbs(osc, f"app.Acquisition.C4.VerScale = 0.5")
    # vbs(osc, f"app.Acquisition.Horizontal.SampleRate = 100e6")
    # vbs(osc, "app.Acquisition.C4.Offset = 0")
    # vbs(osc, "app.Acquisition.C4.View = true")
    # vbs(osc, "app.Acquisition.Trigger.Source = \"C4\"")
    # osc.write("TRIG_MODE Auto")  # 对连续信号建议使用 AUTO 触发模式

#-------------------------------------------------------------------------------

    # osc.write("SINGLE")

if __name__ == "__main__":
    rm = ResourceManager()
    print(sg.frequency)
    try:
        osc = rm.open_resource(OSC_ADDRESS)
        osc.timeout = 50000
        print("✅ Connected to:", osc.query("*IDN?"))
        configure_oscilloscope_for_burst(osc)
        # time.sleep(1)\
        Burst_generate(sg, **SIGNAL_PARAMS)
        # Continuous_generate(sg, **SIGNAL_PARAMS)
        # Trigger_generate(sg, **SIGNAL_PARAMS)
        print("Triggering signal generator...")
        # osc.write("TRIG_MODE Stop")

        # time.sleep(1)
        # osc.write("C1:WF? DAT1")
        # raw_data = osc.query_binary_values("C1:WF? DAT1", datatype="B", container=np.array)

        # scale = float(osc.query("C1:VDIV?").strip().split(" ")[1])
        # v_offset = float(osc.query("C1:OFST?").strip().split(" ")[1])
        # scale1 = 1/30
        # voltages = ((raw_data - 128) * scale + v_offset - 128) * scale1

        # time_div = float(osc.query("TDIV?").strip().split(" ")[1])
        # num_points = len(raw_data)
        # time_span = 10 * time_div  # 总时间范围（10格）
        # # dt = time_span / num_points  # 每个点的时间间隔
        # time_values = np.linspace(0, time_span, num_points, endpoint=False)

        # filename = f"test.csv"
        # scan_folder = os.path.join(data_dir, 'data')
        # file_path = os.path.join(data_dir, filename)
        # df = pd.DataFrame({"Time (s)": time_values, "Amplitude (V)": voltages})
        # df.to_csv(file_path, index=False)
        # print(f"✅ Data saved to: {file_path}")

    except Exception as e:
        print("❌ Error:", e)
    finally:
        if 'osc' in locals():
            osc.close()
            print("✅ Connection closed.")
