import os

import yamcs.pymdb as MDB

rover = MDB.System("Rover")

# Create subsystems for organizing telemetry and telecommands (TMTC)
system_subsystem = MDB.Subsystem(rover, "system", short_description="System-level TMTC")
power_subsystem = MDB.Subsystem(rover, "power", short_description="Power management TMTC")
motor_subsystem = MDB.Subsystem(rover, "motor", short_description="Motor and drive TMTC")
camera_subsystem = MDB.Subsystem(rover, "camera", short_description="Camera control TMTC")
payload_subsystem = MDB.Subsystem(rover, "payload", short_description="Payload configuration TMTC")

# Create sub-subsystems for organizing camera-specific telemetry
images_depth_subsystem = MDB.Subsystem(
    camera_subsystem,
    "images_depth",
    short_description="Depth camera image metadata",
)
images_oncommand_subsystem = MDB.Subsystem(
    camera_subsystem,
    "images_oncommand",
    short_description="On-command capture metadata",
)
images_streaming_subsystem = MDB.Subsystem(
    camera_subsystem,
    "images_streaming",
    short_description="Streaming capture metadata",
)
images_apxs_subsystem = MDB.Subsystem(
    payload_subsystem,
    "images_apxs",
    short_description="APXS capture metadata",
)

###################
#### Telemetry ####
###################

# Payload: Neutron Spectrometer 
neutron_counts = MDB.IntegerParameter(
    system=rover,
    name="neutron_counts",
    signed=True,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Neutron spectrometer counts",
    units="counts",
)

# On Board Computer
obc_state = MDB.EnumeratedParameter(
    system=rover,
    name="obc_state",
    choices=[
        (0, "OFF"),
        (1, "BOOT"),
        (2, "IDLE"),
        (3, "CAMERA"),
        (4, "MOTOR"),
        (5, "SAFE"),
        (6, "ERROR"),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="On-Board Computer state",
)

obc_cpu_usage = MDB.IntegerParameter(
    system=rover,
    name="obc_cpu_usage",
    signed=False,
    bits=8,
    minimum=0,
    maximum=100,
    data_source=MDB.DataSource.LOCAL,
    short_description="On-Board Computer CPU usage",
    units="%",
)

obc_ram_usage = MDB.IntegerParameter(
    system=rover,
    name="obc_ram_usage",
    signed=False,
    bits=8,
    minimum=0,
    maximum=100,
    data_source=MDB.DataSource.LOCAL,
    short_description="On-Board Computer RAM usage",
    units="%",
)

obc_disk_usage = MDB.IntegerParameter(
    system=rover,
    name="obc_disk_usage",
    signed=False,
    bits=8,
    minimum=0,
    maximum=100,
    data_source=MDB.DataSource.LOCAL,
    short_description="On-Board Computer disk usage",
    units="%",
)

obc_uptime = MDB.FloatParameter(
    system=rover,
    name="obc_uptime",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="On-Board Computer uptime",
    units="s",
)

# Mission Status
go_nogo = MDB.EnumeratedParameter(
    system=rover,
    name="go_nogo",
    choices=[
        (0, "NOGO"),
        (1, "GO"),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Current GO/NOGO mission status",
)

solar_panel_state = MDB.EnumeratedParameter(
    system=rover,
    name="solar_panel_state",
    choices=[
        (0, "STOWED"),
        (1, "DEPLOYED"),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Deployment state of the solar panel",
)


# Ground Truth Pose: position (x, y, z) and orientation (w, x, y, z)
pose_ground_truth = MDB.AggregateParameter(
    system=rover,
    name="pose_ground_truth",
    members=[
        MDB.AggregateMember(
            name="position",
            members=[
                MDB.FloatMember(
                    name="x",
                    bits=32,
                    units="m",
                    short_description="X coordinate",
                ),
                MDB.FloatMember(
                    name="y",
                    bits=32,
                    units="m",
                    short_description="Y coordinate",
                ),
                MDB.FloatMember(
                    name="z",
                    bits=32,
                    units="m",
                    short_description="Z coordinate",
                ),
            ],
            short_description="3D position in Cartesian coordinates",
        ),
        MDB.AggregateMember(
            name="orientation",
            members=[
                MDB.FloatMember(
                    name="w",
                    bits=32,
                    short_description="Quaternion W (scalar component)",
                ),
                MDB.FloatMember(
                    name="x",
                    bits=32,
                    short_description="Quaternion X component",
                ),
                MDB.FloatMember(
                    name="y",
                    bits=32,
                    short_description="Quaternion Y component",
                ),
                MDB.FloatMember(
                    name="z",
                    bits=32,
                    short_description="Quaternion Z component",
                ),
            ],
            short_description="3D orientation as quaternion (w, x, y, z)",
        ),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Ground truth pose with position and orientation",
)


# IMU
orientation = MDB.AggregateParameter(
    system=rover,
    name="imu_orientation",
    members=[
        MDB.FloatMember(
            name="roll",
            bits=32,
            units="deg",
        ),
        MDB.FloatMember(
            name="pitch",
            bits=32,
            units="deg",
        ),
        MDB.FloatMember(
            name="yaw",
            bits=32,
            units="deg",
        ),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Orientation data with roll, pitch, and yaw",
)

accelerometer = MDB.AggregateParameter(
    system=rover,
    name="imu_accelerometer",
    members=[
        MDB.FloatMember(
            name="ax",
            bits=32,
            units="m/s^2",
        ),
        MDB.FloatMember(
            name="ay",
            bits=32,
            units="m/s^2",
        ),
        MDB.FloatMember(
            name="az",
            bits=32,
            units="m/s^2",
        ),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Accelerometer data with x, y, z components",
)

gyroscope = MDB.AggregateParameter(
    system=rover,
    name="imu_gyroscope",
    members=[
        MDB.FloatMember(
            name="gx",
            bits=32,
            units="deg/s",
        ),
        MDB.FloatMember(
            name="gy",
            bits=32,
            units="deg/s",
        ),
        MDB.FloatMember(
            name="gz",
            bits=32,
            units="deg/s",
        ),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Gyroscope data with x, y, z components",
)

# Camera depth image metadata
images_depth_url_storage = MDB.StringParameter(
    system=images_depth_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for depth captures",
)

images_depth_url_full = MDB.StringParameter(
    system=images_depth_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for depth captures",
)

images_depth_url_full_nginx = MDB.StringParameter(
    system=images_depth_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for depth captures",
)

images_depth_number = MDB.IntegerParameter(
    system=images_depth_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for depth captures",
)

images_depth_name = MDB.StringParameter(
    system=images_depth_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the depth capture",
)

# Camera on-command image metadata
images_oncommand_url_storage = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for on-command captures",
)

images_oncommand_url_full = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for on-command captures",
)

images_oncommand_url_full_nginx = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for on-command captures",
)

images_oncommand_number = MDB.IntegerParameter(
    system=images_oncommand_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for on-command captures",
)

images_oncommand_name = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the on-command capture",
)

# Camera streaming image metadata
images_streaming_url_storage = MDB.StringParameter(
    system=images_streaming_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for streaming captures",
)

images_streaming_url_full = MDB.StringParameter(
    system=images_streaming_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for streaming captures",
)

images_streaming_url_full_nginx = MDB.StringParameter(
    system=images_streaming_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for streaming captures",
)

images_streaming_number = MDB.IntegerParameter(
    system=images_streaming_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for streaming captures",
)

images_streaming_name = MDB.StringParameter(
    system=images_streaming_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the streaming capture",
)

images_streaming_state = MDB.EnumeratedParameter(
    system=images_streaming_subsystem,
    name="state",
    choices=[
        (0, "OFF"),
        (1, "ON"),
    ],
    data_source=MDB.DataSource.LOCAL,
    short_description="Streaming pipeline state",
)

# Camera APXS image metadata
images_apxs_url_storage = MDB.StringParameter(
    system=images_apxs_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for APXS captures",
)

images_apxs_url_full = MDB.StringParameter(
    system=images_apxs_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for APXS captures",
)

images_apxs_url_full_nginx = MDB.StringParameter(
    system=images_apxs_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for APXS captures",
)

images_apxs_number = MDB.IntegerParameter(
    system=images_apxs_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for APXS captures",
)

images_apxs_name = MDB.StringParameter(
    system=images_apxs_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the APXS capture",
)

# Motors
motor_current = MDB.ArrayParameter(
    system=rover,
    name="motor_current",
    data_type=MDB.FloatDataType(bits=32, units="A"),
    length=6,
    data_source=MDB.DataSource.LOCAL,
    short_description="Array of motor current readings for the six wheels",
)

motor_encoder = MDB.ArrayParameter(
    system=rover,
    name="motor_encoder",
    data_type=MDB.IntegerDataType(signed=False, bits=16, minimum=0, maximum=1024, units="counts"),
    length=6,
    data_source=MDB.DataSource.LOCAL,
    short_description="Array of motor encoder positions for the six wheels",
)

# Radio
radio_rssi = MDB.IntegerParameter(
    system=rover,
    name="radio_rssi",
    signed=True,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Radio signal strength indicator",
    units="dBm",
)

# Thermal
temperature_front = MDB.FloatParameter(
    system=rover,
    name="temperature_front",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Front temperature in Celsius",
    units="C",
)

temperature_back = MDB.FloatParameter(
    system=rover,
    name="temperature_back",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Back temperature in Celsius",
    units="C",
)

temperature_left = MDB.FloatParameter(
    system=rover,
    name="temperature_left",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Left temperature in Celsius",
    units="C",
)

temperature_right = MDB.FloatParameter(
    system=rover,
    name="temperature_right",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Right temperature in Celsius",
    units="C",
)

temperature_top = MDB.FloatParameter(
    system=rover,
    name="temperature_top",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Top temperature in Celsius",
    units="C",
)

temperature_bottom = MDB.FloatParameter(
    system=rover,
    name="temperature_bottom",
    bits=32,
    minimum=-273.15,
    data_source=MDB.DataSource.LOCAL,
    short_description="Bottom temperature in Celsius",
    units="C",
)

temperature_elec_box = MDB.FloatParameter(
    system=rover,
    name="temperature_elec_box",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Electronics box temperature in Celsius",
    units="C",
)

# Power
battery_voltage = MDB.FloatParameter(
    system=rover,
    name="battery_voltage",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Battery voltage",
    units="V",
)

battery_charge = MDB.IntegerParameter(
    system=rover,
    name="battery_charge",
    signed=False,
    bits=8,
    minimum=0,
    maximum=100,
    data_source=MDB.DataSource.LOCAL,
    short_description="Battery charge percentage",
    units="%",
)

total_current_in = MDB.FloatParameter(
    system=rover,
    name="total_current_in",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Total current flowing into the system",
    units="A",
)

total_current_out = MDB.FloatParameter(
    system=rover,
    name="total_current_out",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Total current flowing out of the system",
    units="A",
)

current_draw_obc = MDB.FloatParameter(
    system=rover,
    name="current_draw_obc",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by On-Board Computer",
    units="A",
)

current_draw_motor_controller = MDB.FloatParameter(
    system=rover,
    name="current_draw_motor_controller",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Motor Controller",
    units="A",
)

current_draw_neutron_spectrometer = MDB.FloatParameter(
    system=rover,
    name="current_draw_neutron_spectrometer",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Neutron Spectrometer",
    units="A",
)

current_draw_apxs = MDB.FloatParameter(
    system=rover,
    name="current_draw_apxs",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Alpha Particle X-ray Spectrometer",
    units="A",
)

current_draw_camera = MDB.FloatParameter(
    system=rover,
    name="current_draw_camera",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Camera system",
    units="A",
)

current_draw_radio = MDB.FloatParameter(
    system=rover,
    name="current_draw_radio",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Radio system",
    units="A",
)

current_draw_eps = MDB.FloatParameter(
    system=rover,
    name="current_draw_eps",
    bits=32,
    minimum=0.0,
    data_source=MDB.DataSource.LOCAL,
    short_description="Current consumed by Electric Power System",
    units="A",
)

######################
#### Telecommands ####
######################

# System-level commands (deployments, reboot, go/nogo)

# Solar panel
deploy_arg = MDB.EnumeratedArgument(
    name="deployment",
    choices=[(0, "STOW"), (1, "DEPLOY")],
    short_description="Deployment action",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

deploy_solar_panel = MDB.Command(
    system=system_subsystem,
    name="deploy_solar_panel",
    arguments=[deploy_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"deploy_solar_panel",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=deploy_arg,
            short_description="Deployment action argument",
        ),
    ],
    short_description="Deploy the solar panel",
)

# Reboot
reboot_mode_arg = MDB.EnumeratedArgument(
    name="reboot_mode",
    choices=[(0, "SOFT"), (1, "HARD"), (2, "SAFE_MODE")],
    short_description="Reboot mode",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

reboot_rover = MDB.Command(
    system=system_subsystem,
    name="reboot_rover",
    arguments=[reboot_mode_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"reboot_rover",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=reboot_mode_arg,
            short_description="Reboot mode argument",
        ),
    ],
    short_description="Reboot the rover on-board computer",
)

# Deploy from lander
deploy_from_lander = MDB.Command(
    system=system_subsystem,
    name="deploy_from_lander",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"deploy_from_lander",
            short_description="Command name identifier",
        )
    ],
    short_description="Deploy rover from lander platform",
)

# GO/NOGO decision
go_nogo_decision_arg = MDB.EnumeratedArgument(
    name="decision",
    choices=[(0, "NOGO"), (1, "GO")],
    short_description="GO/NOGO decision",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

go_nogo_command = MDB.Command(
    system=system_subsystem,
    name="go_nogo_command",
    arguments=[go_nogo_decision_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"go_nogo_command",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=go_nogo_decision_arg,
            short_description="GO/NOGO decision argument",
        ),
    ],
    short_description="GO/NOGO decision",
)


# Motor commands

linear_velocity_arg = MDB.FloatArgument(
    name="linear_velocity",
    bits=32,
    units="m/s",
    short_description="Linear velocity",
    encoding=MDB.FloatEncoding(bits=32)
)

distance_arg = MDB.FloatArgument(
    name="distance",
    bits=32,
    units="m",
    short_description="Distance to travel",
    encoding=MDB.FloatEncoding(bits=32)
)

drive_straight = MDB.Command(
    system=motor_subsystem,
    name="drive_straight",
    arguments=[linear_velocity_arg, distance_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"drive_straight",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=linear_velocity_arg,
            short_description="Linear velocity argument",
        ),
        MDB.ArgumentEntry(
            argument=distance_arg,
            short_description="Distance argument",
        ),
    ],
    short_description="Drive the rover straight",
)

angular_velocity_arg = MDB.FloatArgument(
    name="angular_velocity",
    bits=32,
    units="deg/s",
    short_description="Angular velocity",
    encoding=MDB.FloatEncoding(bits=32)
)

angle_arg = MDB.FloatArgument(
    name="angle",
    bits=32,
    units="deg",
    short_description="Angle to turn",
    encoding=MDB.FloatEncoding(bits=32)
)

drive_turn = MDB.Command(
    system=motor_subsystem,
    name="drive_turn",
    arguments=[angular_velocity_arg, angle_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"drive_turn",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=angular_velocity_arg,
            short_description="Angular velocity argument",
        ),
        MDB.ArgumentEntry(
            argument=angle_arg,
            short_description="Angle argument",
        ),
    ],
    short_description="Drive the rover with spot turn",
)

# Camera commands

camera_streaming_arg = MDB.EnumeratedArgument(
    name="action",
    choices=[(0, "STOP"), (1, "START")],
    short_description="Camera streaming action",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

camera_streaming = MDB.Command(
    system=camera_subsystem,
    name="camera_streaming",
    arguments=[camera_streaming_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"camera_streaming",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=camera_streaming_arg,
            short_description="Camera action argument",
        ),
    ],
    short_description="Start or stop camera streaming",
)

camera_capture_high = MDB.Command(
    system=camera_subsystem,
    name="camera_capture_high",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"camera_capture_high",  # Command name as bytes
            short_description="Command name identifier",
        )
    ],
    short_description="Capture a high-resolution image",
)

camera_capture_depth = MDB.Command(
    system=camera_subsystem,
    name="camera_capture_depth",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"camera_capture_depth",  # Command name as bytes
            short_description="Command name identifier",
        )
    ],
    short_description="Capture a depth image",
)

# Camera settings: single config file path argument
config_path_arg = MDB.StringArgument(
    name="config_path",
    short_description="Path to the configuration file",
    encoding=MDB.StringEncoding()
)

change_camera_settings = MDB.Command(
    system=camera_subsystem,
    name="change_camera_settings",
    arguments=[config_path_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"change_camera_settings",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=config_path_arg,
            short_description="Configuration file path argument",
        ),
    ],
    short_description="Change the camera settings with a config file",
)

# Payload commands

payload_config_path_arg = MDB.StringArgument(
    name="config_path",
    short_description="Path to the configuration file",
    encoding=MDB.StringEncoding()
)

change_payload_settings = MDB.Command(
    system=payload_subsystem,
    name="change_payload_settings",
    arguments=[payload_config_path_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"change_payload_settings",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=payload_config_path_arg,
            short_description="Configuration file path argument",
        ),
    ],
    short_description="Change the payload settings with a config file",
)

payload_capture_apxs = MDB.Command(
    system=payload_subsystem,
    name="payload_capture_apxs",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"payload_capture_apxs",
            short_description="Command name identifier",
        )
    ],
    short_description="Capture an Alpha Particle X-ray Spectroscopy measurement",
)

# Power commands

subsystem_id_arg = MDB.EnumeratedArgument(
    name="subsystem_id",
    choices=[
        (0, "CAMERA"),
        (1, "MOTOR_CONTROLLER"),
        (2, "NEUTRON_SPECTROMETER"),
        (3, "APXS"),
        (4, "RADIO"),
    ],
    short_description="Subsystem identifier",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

power_state_arg = MDB.EnumeratedArgument(
    name="power_state",
    choices=[(0, "OFF"), (1, "ON")],
    short_description="Power state",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED)
)

power_electronics = MDB.Command(
    system=power_subsystem,
    name="power_electronics",
    arguments=[subsystem_id_arg, power_state_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"power_electronics",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=subsystem_id_arg,
            short_description="Subsystem ID argument",
        ),
        MDB.ArgumentEntry(
            argument=power_state_arg,
            short_description="Power state argument",
        ),
    ],
    short_description="Power on/off electronics subsystems",
)

# Emit an XML that conforms to XTCE
# print(rover.dumps())
# Save it to yamcs-server source tree (overwriting existing file)
output_path = f"{os.path.dirname(__file__)}/../yamcs-server/src/main/yamcs/mdb/rover.xml"
with open(output_path, "wt") as f:
    rover.dump(f)