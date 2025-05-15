# Signal Generator Configuration
import time

def Continuous_generate(
    sg, 
    shape=None, 
    frequency=None, 
    amplitude=None, 
    offset=None,
    phase=None,
    pulse_dutycycle = None,
    square_dutycycle = None,
    **kwargs
):   
    # 1. Restore continuous mode
    sg.burst_state = False
    sg.arb_advance = "SRAT"  # Set to sample rate advance mode (continuous playback)
    sg.trigger_source = "IMM"  # Set to immediate trigger mode (no external trigger)
    
    # 2. Optionally update waveform parameters
    if shape:
        sg.shape = shape
    if pulse_dutycycle:
        sg.pulse_dutycycle = pulse_dutycycle
    if frequency:
        sg.frequency = frequency
    if amplitude:
        sg.amplitude = amplitude
    if offset:
        sg.offset = offset
    if phase:
        sg.phase = phase
    if square_dutycycle:
        sg.square_dutycycle = square_dutycycle  

    sg.output = True

    print("✅ Signal generator set to continuous mode.")
    print(f"""Waveform: {sg.shape}, 
Frequency: {sg.frequency} Hz, 
Amplitude: {sg.amplitude} V, 
Offset: {sg.offset} V, 
Phase: {sg.phase} degrees""")
    
def Burst_generate_sine(
    sg,
    frequency,
    amplitude,
    burst_ncycles,
    shape="None",
    number_of_burst=1,
    offset=0,
    phase=0,
    burst_period=None
):
    # 1. Set burst mode
    sg.burst_mode = "TRIG"
    sg.burst_state = True
    sg.trigger_source = "BUS"

    # 2. Set waveform parameters
    if shape:
        sg.shape = shape
    sg.frequency = frequency
    sg.amplitude = amplitude
    sg.burst_ncycles = burst_ncycles
    sg.offset = offset
    sg.phase = phase

    # 3. Auto-compute burst_period if not provided
    burst_period = 1.2*burst_ncycles / frequency if frequency and burst_ncycles else 1

    # 4. Enable output
    sg.output = True

    # 5. Burst triggering loop
    for i in range(number_of_burst):
        sg.trigger()
        sg.wait_for_trigger(timeout=burst_period)
        sg.beep()

    # 6. Print config
    print("✅ SINE waveform burst generated.")
    print(f"""Frequency: {sg.frequency} Hz, 
Amplitude: {sg.amplitude} V,
Burst cycles: {sg.burst_ncycles},
Number of bursts: {number_of_burst}, 
Offset: {sg.offset} V, 
Phase: {sg.phase}°,
Burst period: {sg.burst_period} s""")




def Trigger_generate(
    sg, 
    shape="None",
    frequency=None, 
    amplitude=None, 
    number_of_trigger=None,
    pulse_dutycycle = None,
    offset=None,
    phase=None
):
    # 1. Set mode to triggered output
    sg.arb_advance = "TRIG"
    # sg.burst_state = False
    sg.trigger_source = "BUS"
    
    # 2. Optionally update waveform parameters
    if shape:
        sg.shape = shape
    if frequency:
        sg.frequency = frequency
    if amplitude:
        sg.amplitude = amplitude
    if offset:
        sg.offset = offset
    if pulse_dutycycle:
        sg.pulse_dutycycle = pulse_dutycycle
    if phase:
        sg.phase = phase 

    sg.output = True

    sg.trigger()
    sg.wait_for_trigger(timeout=10)
    sg.beep()  

    print("✅ Signal generator executed triggered mode.")
    print(f"""Waveform: {sg.shape}, 
Frequency: {sg.frequency} Hz, 
Amplitude: {sg.amplitude} V, 
Offset: {sg.offset} V, 
Phase: {sg.phase} degrees""")


def Burst_generate(
    sg,
    shape="None",
    frequency=None, 
    amplitude=None, 
    burst_ncycles=None,
    number_of_burst=None,
    offset=None,
    phase=None,
    burst_period = None,
    pulse_width = None,
    pulse_transition = None,
    square_dutycycle = None,
    **kwargs
):
    # 1. Set burst mode
    sg.burst_mode = "TRIG"
    sg.burst_state = True
    sg.trigger_source = "BUS"
    
    # 2. Optionally update waveform parameters
    if shape:
        sg.shape = shape
    if frequency:
        sg.frequency = frequency
    if amplitude:
        sg.amplitude = amplitude
    if burst_ncycles:
        sg.burst_ncycles = burst_ncycles
    if offset:
        sg.offset = offset
    if phase:
        sg.phase = phase 
    if pulse_width:
        sg.pulse_width = pulse_width
    if burst_period:
        sg.burst_period = burst_period
    if pulse_transition:
        sg.pulse_transition = pulse_transition
    if square_dutycycle:
        sg.square_dutycycle = square_dutycycle

    # Estimate burst period based on cycles and frequency
    # # if shape == "SIN" and frequency and burst_ncycles:
    # burst_period = burst_ncycles / frequency if frequency and burst_ncycles else 1

    # # # if shape == "PULS" and pulse_width and burst_ncycles:
    # burst_period = burst_ncycles * pulse_width

    # Estimate burst_period only if not provided
    if not burst_period and burst_ncycles:
        shape = shape.upper() if shape else ""
        if shape in ["SIN", "SINE", "SQUARE", "TRIANGLE", "RAMP"] and frequency:
            burst_period = burst_ncycles / frequency if frequency and burst_ncycles else 1
        elif shape == "PULS" and pulse_width:
            burst_period = burst_ncycles * pulse_width
        else:
            burst_period = 1  # fallback value



    sg.output = True
    # time.sleep(0.2)

    if not number_of_burst:
        number_of_burst = 1  # Default to one trigger if not specified

    for i in range(number_of_burst):
        # sg.wait_for_trigger(timeout=burst_period)
        sg.trigger()
        # sg.wait_for_trigger(timeout=burst_period) #burst_period
        # sg.beep()

    print("✅ Signal generator set to burst mode.")
    print(f"""Waveform: {sg.shape}, 
Frequency: {sg.frequency} Hz, 
Amplitude: {sg.amplitude} V,
Burst cycles: {sg.burst_ncycles},
Number of bursts: {number_of_burst}, 
Offset: {sg.offset} V, 
Phase: {sg.phase} degrees""")


# Prompt to stop signal generation
def stop_condition():
    input("Press Enter to stop signal generation...")
    return True

# Stop output
def stop_output(sg):
    stop_condition()
    sg.output = False
    print("⚠️ Signal output stopped.")

# Wait for trigger (blocking)
def stop_trigger(sg):
    sg.wait_for_trigger()

# Wait for burst to complete or manual stop
def stop_burst(sg, burst_period):
    sg.wait_for_trigger(timeout=burst_period, should_stop=stop_condition)
