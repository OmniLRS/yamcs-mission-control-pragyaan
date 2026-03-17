import os

import yamcs.pymdb as MDB

lander = MDB.System("Lander")

camera_subsystem = MDB.Subsystem(lander, "camera", short_description="Lander camera telemetry")
images_oncommand_subsystem = MDB.Subsystem(
    camera_subsystem,
    "images_oncommand",
    short_description="On-command capture metadata",
)

###################
#### Telemetry ####
###################

images_oncommand_url_storage = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_storage",
    data_source=MDB.DataSource.LOCAL,
    short_description="Storage endpoint for lander captures",
)

images_oncommand_url_full = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_full",
    data_source=MDB.DataSource.LOCAL,
    short_description="External URL for lander captures",
)

images_oncommand_url_full_nginx = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="url_full_nginx",
    data_source=MDB.DataSource.LOCAL,
    short_description="NGINX reverse proxy URL for lander captures",
)

images_oncommand_number = MDB.IntegerParameter(
    system=images_oncommand_subsystem,
    name="number",
    signed=False,
    bits=32,
    data_source=MDB.DataSource.LOCAL,
    short_description="Sequence identifier for lander captures",
)

images_oncommand_name = MDB.StringParameter(
    system=images_oncommand_subsystem,
    name="name",
    data_source=MDB.DataSource.LOCAL,
    short_description="Friendly name for the lander capture",
)

######################
#### Telecommands ####
######################

lander_camera_capture = MDB.Command(
    system=camera_subsystem,
    name="lander_camera_capture",
    arguments=[],
    entries=[
        MDB.FixedValueEntry(
            name="command_name",
            binary=b"lander_camera_capture",
            short_description="Command name identifier",
        ),
    ],
    short_description="Request capture from lander camera",
)

output_path = f"{os.path.dirname(__file__)}/../yamcs-server/src/main/yamcs/mdb/lander.xml"
with open(output_path, "wt") as f:
    lander.dump(f)
