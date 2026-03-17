
import time
import math
from yamcs.client import YamcsClient

# Configuration constants
YAMCS_HOST = "localhost:8090"
YAMCS_INSTANCE = "workshop"
YAMCS_PROCESSOR = "realtime"
SLEEP_INTERVAL = 1  # in seconds

# Parameter configuration
# All parameters use the same recursive structure:
# - Scalar: (min, max, period, offset)
# - Array: [(min, max, period, offset), ...]
# - Aggregate: {member_name: <scalar|array|aggregate>}
# Optional: wrap with {"value_type": "int"} to convert floats to ints
PARAMETER_CONFIG = {
    # Ground Truth Pose (Nested Aggregate: position and orientation)
    "/Rover/pose_ground_truth": {
        "position": {
            "x": (-10.0, 10.0, 50.0, 0.0),   # meters
            "y": (-10.0, 10.0, 55.0, 5.0),   # meters
            "z": (-3.0, 3.0, 60.0, 10.0),    # meters
        },
        "orientation": {
            "w": (0.0, 1.0, 40.0, 0.0),      # quaternion scalar
            "x": (-1.0, 1.0, 42.0, 3.0),     # quaternion x
            "y": (-1.0, 1.0, 44.0, 6.0),     # quaternion y
            "z": (-1.0, 1.0, 46.0, 9.0),     # quaternion z
        }
    },
    
    # IMU - Orientation, Accelerometer, Gyroscope (Aggregates)
    "/Rover/imu_orientation": {
        "roll": (-180.0, 180.0, 20.0, 0.0),
        "pitch": (-90.0, 90.0, 25.0, 3.0),
        "yaw": (-180.0, 180.0, 30.0, 6.0),
    },
    "/Rover/imu_accelerometer": {
        "ax": (-10.0, 10.0, 12.0, 0.0),
        "ay": (-10.0, 10.0, 15.0, 2.0),
        "az": (-10.0, 10.0, 18.0, 4.0),
    },
    "/Rover/imu_gyroscope": {
        "gx": (-180.0, 180.0, 10.0, 0.0),
        "gy": (-180.0, 180.0, 15.0, 2.5),
        "gz": (-180.0, 180.0, 20.0, 5.0),
    },
    
    # Motors - Current (Array of 6 floats)
    "/Rover/motor_current": [
        (0.0, 2.0, 8.0, 0.0),    # Motor 0
        (0.0, 2.0, 8.5, 1.0),    # Motor 1
        (0.0, 2.0, 9.0, 2.0),    # Motor 2
        (0.0, 2.0, 9.5, 3.0),    # Motor 3
        (0.0, 2.0, 10.0, 4.0),   # Motor 4
        (0.0, 2.0, 10.5, 5.0),   # Motor 5
    ],
    
    # Motors - Encoder positions (Array of 6 ints)
    "/Rover/motor_encoder": {
        "value_type": "int",
        "value": [
            (0, 1024, 12.0, 0),      # Motor 0
            (0, 1024, 12.5, 1.5),    # Motor 1
            (0, 1024, 13.0, 3.0),    # Motor 2
            (0, 1024, 13.5, 4.5),    # Motor 3
            (0, 1024, 14.0, 6.0),    # Motor 4
            (0, 1024, 14.5, 7.5),    # Motor 5
        ]
    },
    
    # Radio - Signal strength (Scalar int)
    "/Rover/radio_rssi": {
        "value_type": "int",
        "value": (-100, -30, 30, 0),  # dBm range
    },
    
    # Power - Battery voltage (Scalar float)
    "/Rover/battery_voltage": (11.0, 17.0, 45.0, 0.0),  # Volts
    
    # Power - Battery charge percentage (Scalar int)
    "/Rover/battery_charge": {
        "value_type": "int",
        "value": (0, 100, 60, 0),  # Percentage
    },
    
    # Power - Current in and out (Scalar floats)
    "/Rover/total_current_in": (0.0, 10.0, 35.0, 0.0),  # Amps
    "/Rover/total_current_out": (0.0, 15.0, 40.0, 5.0),  # Amps
    
    # Power - Current draw by subsystems (Scalar floats)
    "/Rover/current_draw_obc": (0., 1.5, 25.0, 0.0),
    "/Rover/current_draw_motor_controller": (0., 1.0, 30.0, 2.0),
    "/Rover/current_draw_neutron_spectrometer": (0., 1.8, 45.0, 3.0),
    "/Rover/current_draw_apxs": (0., 1.8, 40.0, 4.0),
    "/Rover/current_draw_camera": (0., 1.0, 35.0, 5.0),
    "/Rover/current_draw_radio": (0., 1.0, 28.0, 6.0),
    "/Rover/current_draw_eps": (0., 0.2, 50.0, 7.0),
    
    # Payload - Neutron Spectrometer (Scalar int)
    "/Rover/neutron_counts": {
        "value_type": "int",
        "value": (0, 250, 20.0, 0.0),  # counts
    },
    
    # Temperature sensors (Scalar floats in Celsius)
    "/Rover/temperature_front": (-50.0, 100.0, 55.0, 0.0),     # °C - Front panel
    "/Rover/temperature_back": (-50.0, 100.0, 58.0, 1.5),      # °C - Back panel
    "/Rover/temperature_left": (-50.0, 100.0, 52.0, 3.0),      # °C - Left panel
    "/Rover/temperature_right": (-50.0, 100.0, 56.0, 4.5),     # °C - Right panel
    "/Rover/temperature_top": (-50.0, 100.0, 60.0, 6.0),       # °C - Top panel
    "/Rover/temperature_bottom": (-50.0, 100.0, 54.0, 7.5),    # °C - Bottom panel
    "/Rover/temperature_elec_box": (-50.0, 100.0, 48.0, 9.0),    # °C - Electronics box
    
    # On-Board Computer monitoring
    "/Rover/obc_state": {
        "value_type": "int",
        "value": (0, 6, 6.0, 0.0),  # State enum 0-6
    },
    "/Rover/obc_cpu_usage": {
        "value_type": "int",
        "value": (10, 90, 25.0, 0.0),  # CPU usage %
    },
    "/Rover/obc_ram_usage": {
        "value_type": "int",
        "value": (30, 85, 30.0, 2.0),  # RAM usage %
    },
    "/Rover/obc_disk_usage": {
        "value_type": "int",
        "value": (40, 95, 120.0, 5.0),  # Disk usage % (slow change)
    },
    "/Rover/obc_uptime": (0.0, 86400.0, 300.0, 0.0),  # Uptime in seconds (0-24h range, 5min period)
    
    # Mission Status
    "/Rover/go_nogo": {
        "value_type": "int",
        "value": (0, 1, 5.0, 0.0),  # GO/NOGO status (0=NOGO, 1=GO), slow toggle
    },
}


def generate_sine_value(t, min_val, max_val, period, offset):
    """Generate a sine wave value at time t with given parameters."""
    omega = 2 * math.pi / period
    amplitude = (max_val - min_val) / 2
    center = (max_val + min_val) / 2
    return center + amplitude * math.sin(omega * (t + offset))


def process_value(t, structure, value_type="float"):
    """Recursively process any parameter structure.
    
    Args:
        t: Current time value
        structure: Can be:
            - tuple (min, max, period, offset): scalar value
            - list of tuples: array of values
            - dict with "value_type" and "value": typed wrapper
            - dict without those keys: aggregate with named members
        value_type: "float" or "int" for numeric conversion
        
    Returns:
        Processed value (scalar, list, or dict)
    """
    # Handle typed wrapper: {"value_type": "int", "value": ...}
    if isinstance(structure, dict) and "value_type" in structure:
        return process_value(t, structure["value"], structure["value_type"])
    
    # Handle tuple: scalar value (min, max, period, offset)
    if isinstance(structure, tuple) and len(structure) == 4:
        value = generate_sine_value(t, *structure)
        return int(round(value)) if value_type == "int" else value
    
    # Handle list: array of values
    if isinstance(structure, list):
        values = [generate_sine_value(t, *elem) for elem in structure]
        return [int(round(v)) for v in values] if value_type == "int" else values
    
    # Handle dict: aggregate with named members
    if isinstance(structure, dict):
        return {
            key: process_value(t, value, value_type)
            for key, value in structure.items()
        }
    
    raise ValueError(f"Unexpected structure: {structure}")


def main():
    client = YamcsClient(YAMCS_HOST)
    processor = client.get_processor(instance=YAMCS_INSTANCE, processor=YAMCS_PROCESSOR)
    print("Connected to Yamcs")
    print("Parameters to generate:")
    for param_path in PARAMETER_CONFIG.keys():
        print(f"  {param_path}") 
    print("Starting telemetry generation...")
    t = 0
    while True:
        # Process all parameters in PARAMETER_CONFIG
        parameter_values = {
            param_path: process_value(t, config)
            for param_path, config in PARAMETER_CONFIG.items()
        }
        
        processor.set_parameter_values(parameter_values)
        t += SLEEP_INTERVAL
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
    