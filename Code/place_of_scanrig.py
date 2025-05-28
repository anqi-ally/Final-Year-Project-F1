import socket
from rig_function import send_command

def get_all_positions(sock):
    """
    Retrieve encoder and pulse positions for all axes (X, Y, Z).
    Returns a dictionary in the format:
    {
        "X": {"encoder": ..., "pulse": ...},
        "Y": {"encoder": ..., "pulse": ...},
        "Z": {"encoder": ..., "pulse": ...},
    }
    """
    encoder_resp = send_command(sock, "PE")
    pulse_resp = send_command(sock, "PP")

    try:
        # Response format is expected to be U:X:Y:Z
        encoder_vals = list(map(int, encoder_resp.split(":")))
        pulse_vals = list(map(int, pulse_resp.split(":")))

        return {
            "X": {"encoder": encoder_vals[1], "pulse": pulse_vals[1]},
            "Y": {"encoder": encoder_vals[2], "pulse": pulse_vals[2]},
            "Z": {"encoder": encoder_vals[3], "pulse": pulse_vals[3]},
        }

    except Exception as e:
        print(f"⚠️ Error parsing position response: {e}")
        return None

def print_all_positions(sock):
    """
    Print the current encoder and pulse positions for X/Y/Z axes.
    """
    pos = get_all_positions(sock)

    if pos:
        for axis in ["X", "Y", "Z"]:
            enc = pos[axis]['encoder']
            pulse = pos[axis]['pulse']
            print(f"{axis}-axis: Encoder = {enc}, Pulse = {pulse}")
    else:
        print("⚠️ Failed to retrieve axis positions.")


import socket
from Setup import HOST, PORT

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print_all_positions(s)
