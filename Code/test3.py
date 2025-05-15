import time
from pymeasure.instruments.agilent import Agilent33500
from pyvisa import ResourceManager
from Setup import SIGNAL_PARAMS, WAVEFORM_PARAMS
from Signal_function import Burst_generate, Continuous_generate, Burst_generate_sine
import numpy as np
import os
from const import data_dir
import pandas as pd

# ✅ 连接信号发生器
sg = Agilent33500("USB0::0x0957::0x0407::MY44023097::INSTR")
print("Successfully connected to signal generator:", sg.id)

# ✅ 选择模式
mode = input("请选择模式 (1: Continuous, 2: Burst): ").strip()

shape_choice = input("请选择模式 (1: SIN (正弦波), 2: SQU (方波), 3: PULS (脉冲波)): ").strip()

# ✅ 根据选择生成参数
if shape_choice == "1":
    shape = "SIN"
elif shape_choice == "2":
    shape = "SQU"
elif shape_choice == "3":
    shape = "PULS"
else:
    raise ValueError("❌ 无效波形类型选择")

params = WAVEFORM_PARAMS[shape]

if mode == "1":
    mode = "continuous"
    Continuous_generate(sg, **params)


elif mode == "2":
    mode = "burst"

    Burst_generate(
        sg,
        **params
    )


# 断开连接
sg.shutdown()
print("✅ 所有任务完成！")
