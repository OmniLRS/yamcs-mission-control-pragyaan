import argparse
import os
import shutil


def parse_and_write(system, name: str) -> None:
    """Parse CLI args, write the MDB XML, and optionally deploy it."""
    here = os.path.dirname(os.path.abspath(__file__))
    default_output = f"{here}/../yamcs-server/src/main/yamcs/mdb/{name}.xml"
    default_deploy = f"{here}/../../OmniLRS/cfg/mdb/pragyaan/{name}.xml"

    parser = argparse.ArgumentParser(description=f"Generate the {name} MDB XML.")
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Skip copying the generated XML to the Rover simulation deploy path.",
    )
    parser.add_argument(
        "--deploy-path",
        default=default_deploy,
        help="Override the deploy path for the generated XML.",
    )
    args = parser.parse_args()

    output_path = os.path.abspath(default_output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wt") as f:
        system.dump(f)
    print(f"Wrote {name}.xml MDB for Yamcs Ground Segment to {output_path}")

    if not args.no_deploy:
        deploy_path = os.path.abspath(args.deploy_path)
        os.makedirs(os.path.dirname(deploy_path), exist_ok=True)
        shutil.copyfile(output_path, deploy_path)
        print(f"Deployed {name}.xml MDB for Rover simulation to {deploy_path}")
