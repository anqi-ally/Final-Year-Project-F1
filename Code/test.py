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


if __name__ == "__main__":
    rm = ResourceManager()
    print(sg.frequency)
    try:
        osc = rm.open_resource(OSC_ADDRESS)
        osc.timeout = 50000
        print("✅ Connected to:", osc.query("*IDN?"))
        configure_oscilloscope_for_burst(osc)
        Burst_generate(sg, **SIGNAL_PARAMS)
        print("Triggering signal generator...")

    except Exception as e:
        print("❌ Error:", e)
    finally:
        if 'osc' in locals():
            osc.close()
            print("✅ Connection closed.")
