# ✅ Imports
import time
import socket
from pymeasure.instruments.agilent import Agilent33500
from pyvisa import ResourceManager

# === Custom modules ===
from rig_function import send_command, enable_axis, wait_until_stopped

# ✅ Configuration import
from Setup import A_SCAN_PARAMS

HOST = "192.168.1.250"
PORT = 5001

# ✅ Utility functions
def mm_to_pulse(mm):
    return int(mm * 5600)

# ✅ Main program
def main():
    # Unit conversion: mm to pulse
    A_SCAN_PARAMS["X"] = mm_to_pulse(A_SCAN_PARAMS["X"])
    A_SCAN_PARAMS["Y"] = mm_to_pulse(A_SCAN_PARAMS["Y"])
    A_SCAN_PARAMS["Z"] = mm_to_pulse(A_SCAN_PARAMS["Z"])

    # Establish TCP connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        # Set movement mode
        send_command(sock, "INC")

        # Sequentially enable and move axes X, Y, Z
        for axis in ["X", "Y", "Z"]:
            distance = A_SCAN_PARAMS.get(axis)
            if distance:
                enable_axis(sock, axis)
                send_command(sock, f"{axis}{distance}")
                wait_until_stopped(sock, axis)

    print("✅ A Scan movement complete.")

if __name__ == "__main__":
    main()
