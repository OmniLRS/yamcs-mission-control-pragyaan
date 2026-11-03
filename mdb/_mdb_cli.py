import os


def write_mdb(system, name: str) -> None:
    """Write the MDB XML to yamcs-server/src/main/yamcs/mdb/<name>.xml, where Yamcs loads it at instance start."""
    here = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(f"{here}/../yamcs-server/src/main/yamcs/mdb/{name}.xml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wt") as f:
        system.dump(f)
    print(f"Wrote {name}.xml MDB for Yamcs Ground Segment to {output_path}")
