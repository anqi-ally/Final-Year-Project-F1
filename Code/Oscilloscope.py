import os
import pyvisa
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from const import data_dir
from Signal_function import Burst_generate
from Setup import OSC_ADDRESS, SIGNAL_PARAMS, SCAN_PARAMS

# Create a folder for storing scan data
def create_scan_folder():
    os.makedirs(data_dir, exist_ok=True)
    existing_scans = [d for d in os.listdir(data_dir) if d.startswith('scan_') and os.path.isdir(os.path.join(data_dir, d))]
    scan_numbers = [int(d.split('_')[1]) for d in existing_scans if d.split('_')[1].isdigit()]
    next_scan_num = max(scan_numbers, default=0) + 1
    scan_folder = os.path.join(data_dir, f'scan_{next_scan_num:03d}')
    os.makedirs(scan_folder)
    return scan_folder

# Configure oscilloscope acquisition settings for burst waveform
def configure_oscilloscope_for_burst(osc, SIGNAL_PARAMS):
    """
    Configure oscilloscope acquisition settings for burst waveform capture.
    """
    def vbs(osc, cmd):
        osc.write(f"VBS '{cmd}'")
        time.sleep(0.1)

    freq = SIGNAL_PARAMS["frequency"]
    amp = SIGNAL_PARAMS["amplitude"]
    n_cycles = SIGNAL_PARAMS["burst_ncycles"]

    burst_duration = n_cycles / freq
    hor_scale = burst_duration / 5
    ver_scale = amp
    Sampling_Rate = freq * 100

    vbs(osc, f"app.Acquisition.Horizontal.HorScale = 50e-6")
    vbs(osc, f"app.Acquisition.C4.VerScale = 0.5")
    vbs(osc, f"app.Acquisition.Horizontal.SampleRate = 100e6")
    vbs(osc, "app.Acquisition.C4.Offset = 0")
    vbs(osc, "app.Acquisition.C4.View = true")
    vbs
