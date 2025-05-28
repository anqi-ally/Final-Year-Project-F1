# ▶️ Signal parameters

SIGNAL_PARAMS = {
    "shape": "SQU",
    "frequency": 1e3,
    "amplitude": 3.3,
    "offset": 0,
    "burst_ncycles": 1,
    "square_dutycycle": 50
}

# Preset parameters for each waveform type
WAVEFORM_PARAMS = {
    "SIN": {
        "shape": "SIN",
        "frequency": 1e3,
        "amplitude": 3.3,
        "offset": 0,
        "burst_ncycles": 1
    },
    "SQU": {
        "shape": "SQU",
        "frequency": 1e3,
        "amplitude": 3.3,
        "offset": 0,
        "burst_ncycles": 1,
        "square_dutycycle": 50,
    },
    "PULS": {
        "shape": "PULS",
        "frequency": 1,
        "amplitude": 3.3,
        "offset": 0,
        # "pulse_dutycycle": 10,
        "burst_ncycles": 1,
        # "burst_period": 0.1,
        "pulse_transition": 1e-8,
        "pulse_width": 1e-3
    }
}

# ▶️ Scan parameters for A scan (unit: mm)
A_SCAN_PARAMS = {
    "X": 0,       # mm
    "Y": 0,       # mm
    "Z": 1,       # mm
    "mode": "INC" 
}

# ▶️ Scan parameters for B scan (unit: mm)
SCAN_PARAMS = {
    "scan_axis": "Z",
    "cross_axis": "Y",
    "scan_length": 3,        # mm
    # "scan_step": 0.2,      # mm
    "scan_points": 32,
    "cross_length": 3,       # mm
    # "cross_step": 0.2,     # mm
    "cross_points": 32,
    "start_col": 2,
}

# ▶️ TCP address of the scanning device
HOST = "192.168.1.250"
PORT = 5001

# ▶️ VISA address of the signal generator
SG_ADDRESS = "USB0::0x0957::0x0407::MY44023097::INSTR"  # example: "USB0::0x0957::0x1607::MY50004553::INSTR"

# ▶️ VISA address of the oscilloscope
OSC_ADDRESS = "USB0::0x05FF::0x1023::3502N04522::INSTR"  # example: "USB0::0x05FF::0x1023::3557N06479::INSTR"
