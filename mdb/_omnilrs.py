"""Read the robot definition from an OmniLRS checkout.

The rover cameras are defined in OmniLRS cfg/robot/<robot>.yaml (parsed by src/configurations/robot_camera_confs.py), the
image buckets of its controller in
cfg/controller/<controller>.yaml, the streaming telemetry fields and image resolutions of its transmitter and camera
handler in src/mission_specific/<robot>/tmtc/enums.py, and the rule mapping cameras to MDB paths and storage buckets
in src/tmtc/yamcs_naming.py. All are read from the checkout given by --omnilrs-root or $OMNILRS_ROOT, so the MDB
always matches the OmniLRS commit it is generated from.
"""

import argparse
import importlib.util
import os
import sys

import yaml

# OmniLRS config files this repository is for: cfg/robot/<ROBOT>.yaml and cfg/controller/<CONTROLLER>.yaml
# (file names; the robot name itself is only defined in the robot yaml). The generators take --robot / --controller.
ROBOT = "pragyaan"
CONTROLLER = "pragyaan-controller"


def parse_args(description: str) -> argparse.Namespace:
    """--omnilrs-root, --robot and --controller of a generator."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--omnilrs-root",
        help="OmniLRS checkout to read the robot and controller yaml and src/tmtc/yamcs_naming.py from "
        "(default: $OMNILRS_ROOT)",
    )
    parser.add_argument("--robot", default=ROBOT, help=f"cfg/robot/<robot>.yaml (default: {ROBOT})")
    parser.add_argument(
        "--controller", default=CONTROLLER, help=f"cfg/controller/<controller>.yaml (default: {CONTROLLER})"
    )
    return parser.parse_args()


def omnilrs_root(cli_value: str | None = None) -> str:
    """OmniLRS checkout from the CLI value or $OMNILRS_ROOT."""
    root = cli_value or os.environ.get("OMNILRS_ROOT")
    if not root:
        raise SystemExit(
            "OmniLRS checkout not set: set OMNILRS_ROOT=<path> (generate_mdb_rover.py also takes --omnilrs-root)"
        )
    if not os.path.isdir(os.path.join(root, "cfg", "robot")):
        raise SystemExit(f"{root!r} is not an OmniLRS checkout (no cfg/robot directory)")
    return os.path.abspath(root)


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # registered before running it, as an import would (dataclasses look it up)
    spec.loader.exec_module(module)
    return module


def load_naming(root: str):
    """Import <root>/src/tmtc/yamcs_naming.py by file path."""
    return _load_module("yamcs_naming", os.path.join(root, "src", "tmtc", "yamcs_naming.py"))


def _load_yaml(root: str, *parts: str) -> dict:
    with open(os.path.join(root, "cfg", *parts), encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cameras(root: str, robot: str = ROBOT) -> list:
    """Cameras of cfg/robot/<robot>.yaml (RobotCameraConf: name, prim_path, type, resolutions, has_type), parsed and
    validated by <root>/src/configurations/robot_camera_confs.py (standard library only), loaded by file path."""
    path = os.path.join(root, "src", "configurations", "robot_camera_confs.py")
    config = _load_yaml(root, "robot", f"{robot}.yaml")
    return _load_module("robot_camera_confs", path).parse_cameras(config["robots_settings"]["parameters"].get("camera"))


def load_yamcs_tmtc(root: str, controller: str = CONTROLLER) -> dict:
    """The yamcs_tmtc section of cfg/controller/<controller>.yaml (non-camera buckets)."""
    return _load_yaml(root, "controller", f"{controller}.yaml")["robots_settings"]["yamcs_tmtc"]


def _load_enums(root: str, robot: str):
    """Import <root>/src/mission_specific/<robot>/tmtc/enums.py (standard library only) by file path."""
    return _load_module(f"{robot}_enums", os.path.join(root, "src", "mission_specific", robot, "tmtc", "enums.py"))


def load_streaming_fields(root: str, robot: str = ROBOT) -> tuple[str, ...]:
    """Streaming telemetry fields OmniLRS sends per rgba camera: STREAMING_FIELDS of the robot's tmtc/enums.py."""
    return tuple(_load_enums(root, robot).STREAMING_FIELDS)


def load_kind_resolution(root: str, robot: str = ROBOT) -> dict:
    """Image kind -> robot yaml resolutions key at which OmniLRS snaps it (e.g. streaming -> low): KIND_RESOLUTION of
    the robot's tmtc/enums.py."""
    return {kind: str(resolution) for kind, resolution in _load_enums(root, robot).KIND_RESOLUTION.items()}
