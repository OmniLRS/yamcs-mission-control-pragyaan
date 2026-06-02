import yamcs.pymdb as MDB

from _mdb_cli import parse_and_write

admin_system = MDB.System("Admin")

camera_subsystem = MDB.Subsystem(
    admin_system,
    "camera",
    short_description="Administrative camera metadata",
)

images_monitoring_subsystem = MDB.Subsystem(
    camera_subsystem,
    "images_monitoring",
    short_description="Admin monitoring image metadata",
)

###################
#### Telemetry ####
###################

images_monitoring_url_storage = MDB.StringParameter(
    system=images_monitoring_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for monitoring captures",
)

images_monitoring_url_full = MDB.StringParameter(
    system=images_monitoring_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for monitoring captures",
)

images_monitoring_url_full_nginx = MDB.StringParameter(
    system=images_monitoring_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for monitoring captures",
)

images_monitoring_number = MDB.IntegerParameter(
    system=images_monitoring_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for monitoring captures",
)

images_monitoring_name = MDB.StringParameter(
    system=images_monitoring_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the monitoring capture",
)

######################
#### Telecommands ####
######################

trigger_water_detection_arg = MDB.BooleanArgument(
    name="trigger_water_detection",
    default=True,
    short_description="True for water detection, False to reset",
    encoding=MDB.bool_t,
)

admin_water_detection = MDB.Command(
    system=admin_system,
    name="admin_water_detection",
    arguments=[trigger_water_detection_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"admin_water_detection",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=trigger_water_detection_arg,
            short_description="Water detection trigger flag",
        ),
    ],
    short_description="[ADMIN] Trigger water detection event (facilitator only)",
)

admin_inject_fault = MDB.Command(
    system=admin_system,
    name="admin_inject_fault",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"admin_inject_fault",
            short_description="Command name identifier",
        ),
    ],
    short_description="[ADMIN] Inject a system fault (facilitator only)",
)

battery_percentage_arg = MDB.IntegerArgument(
    name="battery_percentage",
    signed=False,
    bits=8,
    minimum=0,
    maximum=100,
    short_description="Target battery percentage",
    units="%",
    encoding=MDB.IntegerEncoding(bits=8, scheme=MDB.IntegerEncodingScheme.UNSIGNED),
)

admin_set_battery_percentage = MDB.Command(
    system=admin_system,
    name="admin_set_battery_percentage",
    arguments=[battery_percentage_arg],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"admin_set_battery_percentage",
            short_description="Command name identifier",
        ),
        MDB.ArgumentEntry(
            argument=battery_percentage_arg,
            short_description="Battery percentage argument",
        ),
    ],
    short_description="[ADMIN] Set battery percentage (facilitator only)",
)

# ==================================
# Generate the Mission Database XML
# ==================================

parse_and_write(admin_system, "admin")
