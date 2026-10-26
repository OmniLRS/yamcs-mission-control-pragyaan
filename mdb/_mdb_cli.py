import argparse
import os
import shutil
import yaml
from ruamel.yaml import YAML


ROVER_NAME = "pragyaan"

def deploy_buckets(config_path: str, buckets: list, camera_names: list):
    """Deploy buckets to external OmniLRS's controller config. Assume controller .yaml already exists."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    with open(config_path, "r") as f:
        config = yaml.load(f)

    ### handle buckets
    config["robots_settings"]["yamcs_tmtc"]["images"]["buckets"] = buckets

    ### handle params
    params = config["robots_settings"]["yamcs_tmtc"]["parameters"]
    params_to_pop = [
        "camera_streaming_state",
        "camera_bandwidth",
        "camera_packets_sent",
        "camera_packets_lost",
        "camera_decode_errors"
    ]
    for param in params_to_pop:
        if param not in params.keys():
            continue
        
        old_val = params.pop(param)
        for camera_name in camera_names:
            topic = f"/{old_val.split('/')[-1]}"
            new_val = f"{old_val.split(topic)[0]}_{camera_name}{topic}"
            params[f"{param}_{camera_name}"] = new_val
            

    with open(config_path, "w") as f:
        yaml.dump(config, f)

def write_buckets(config_path: str, buckets: list):
    """Write buckets to local src/main/yamcs/etc/yamcs.yaml """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    config["buckets"] = buckets

    with open(config_path, "w") as f:
        yaml.safe_dump(config, f, sort_keys=False)

def parse_and_write(system, name: str, camera_names: list, buckets_controller: list, buckets_etc_yaml: list) -> None:
    """Parse CLI args, write the MDB XML, and optionally deploy it."""
    here = os.path.dirname(os.path.abspath(__file__))
    default_output = f"{here}/../yamcs-server/src/main/yamcs/mdb/{name}.xml"
    default_deploy_mdb = f"{here}/../../OmniLRS/cfg/mdb/{ROVER_NAME}/{name}.xml"
    default_deploy_controller = f"{here}/../../OmniLRS/cfg/controller/{ROVER_NAME}-controller.yaml"
    default_etc_yamcs_output = f"{here}/../yamcs-server/src/main/yamcs/etc/yamcs.yaml"

    parser = argparse.ArgumentParser(description=f"Generate the {name} MDB XML.")
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Skip copying the generated XML to the Rover simulation deploy path.",
    )
    parser.add_argument(
        "--deploy-mdb-path",
        default=default_deploy_mdb,
        help="Override the deploy path for the generated XML.",
    )
    parser.add_argument(
        "--deploy-controller-path",
        default=default_deploy_controller,
        help="Override the deploy path for the controller YAML.",
    )
    parser.add_argument(
        "--yamcs-path",
        default=default_etc_yamcs_output,
        help="Override the etc yamcs path.",
    )
    args = parser.parse_args()

    output_path = os.path.abspath(default_output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wt") as f:
        system.dump(f)
    print(f"Wrote {name}.xml MDB for Yamcs Ground Segment to {output_path}")

    if not args.no_deploy:
        deploy_mdb_path = os.path.abspath(args.deploy_mdb_path)
        os.makedirs(os.path.dirname(deploy_mdb_path), exist_ok=True)
        shutil.copyfile(output_path, deploy_mdb_path)
        print(f"Deployed {name}.xml MDB for Rover simulation to {deploy_mdb_path}")

        deploy_controller_path = os.path.abspath(args.deploy_controller_path)
        deploy_buckets(deploy_controller_path, buckets_controller, camera_names)
        print(f"Deployed buckets for Rover simulation to {deploy_controller_path}")

    write_buckets(args.yamcs_path, buckets_etc_yaml)
    print(f"Wrote buckets to {args.yamcs_path}")