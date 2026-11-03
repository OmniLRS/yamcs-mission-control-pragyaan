"""Read the robot definition from an OmniLRS checkout.

The rover cameras are defined in OmniLRS (cfg/robot/<robot>.yaml), and the rule mapping them to MDB paths
and storage buckets lives in OmniLRS src/tmtc/yamcs_naming.py. Both are read from the checkout given by
--omnilrs-root or $OMNILRS_ROOT, so the MDB always matches the OmniLRS commit it is generated from.
"""

import importlib.util
import os

import yaml

ROBOT_NAME = "pragyaan"
CONTROLLER_NAME = "pragyaan-controller"


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


def load_naming(root: str):
    """Import <root>/src/tmtc/yamcs_naming.py by file path."""
    path = os.path.join(root, "src", "tmtc", "yamcs_naming.py")
    spec = importlib.util.spec_from_file_location("yamcs_naming", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_yaml(root: str, *parts: str) -> dict:
    with open(os.path.join(root, "cfg", *parts), encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cameras(root: str, naming) -> list[dict]:
    """Cameras of cfg/robot/<ROBOT_NAME>.yaml, validated by yamcs_naming.parse_cameras."""
    config = _load_yaml(root, "robot", f"{ROBOT_NAME}.yaml")
    return naming.parse_cameras(config["robots_settings"]["parameters"].get("camera"))


def load_yamcs_tmtc(root: str) -> dict:
    """The yamcs_tmtc section of cfg/controller/<CONTROLLER_NAME>.yaml (non-camera buckets)."""
    return _load_yaml(root, "controller", f"{CONTROLLER_NAME}.yaml")["robots_settings"]["yamcs_tmtc"]
