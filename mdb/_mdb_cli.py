import os

from ruamel.yaml import YAML

HERE = os.path.dirname(os.path.abspath(__file__))
YAMCS_YAML = os.path.abspath(f"{HERE}/../yamcs-server/src/main/yamcs/etc/yamcs.yaml")

# Image buckets are filesystem buckets: one directory of PNG files per bucket, under this directory. Relative paths
# are resolved from where Yamcs runs (target/yamcs), so like dataDir in yamcs.yaml it is removed by `mvn clean`;
# set an absolute path to keep the images.
IMAGE_BUCKETS_DIR = "images"
# Limits sized to keep every image of a mission (the Yamcs default is 100 MB and 1000 objects per bucket).
# Streaming alone is about 1 GB per camera per hour.
IMAGE_BUCKET_MAX_SIZE = 100 * 1024**3  # bytes
IMAGE_BUCKET_MAX_OBJECTS = 1_000_000


def write_mdb(system, name: str) -> None:
    """Write the MDB XML to yamcs-server/src/main/yamcs/mdb/<name>.xml, where Yamcs loads it at instance start."""
    output_path = os.path.abspath(f"{HERE}/../yamcs-server/src/main/yamcs/mdb/{name}.xml")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wt") as f:
        system.dump(f)
    print(f"Wrote {name}.xml MDB for Yamcs Ground Segment to {output_path}")


def write_image_buckets(bucket_names: list[str], prefix: str) -> None:
    """Replace the image buckets (names starting with prefix) of the `buckets` list in etc/yamcs.yaml.

    Other buckets (e.g. stacks) and the comments of the file are kept (round-trip yaml).
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 120
    with open(YAMCS_YAML, encoding="utf-8") as f:
        config = yaml.load(f)
    buckets = config["buckets"]
    for i in reversed(range(len(buckets))):
        if str(buckets[i]["name"]).startswith(prefix):
            del buckets[i]
    for name in bucket_names:
        buckets.append(
            {
                "name": name,
                "path": f"{IMAGE_BUCKETS_DIR}/{name}",
                "maxSize": IMAGE_BUCKET_MAX_SIZE,
                "maxObjects": IMAGE_BUCKET_MAX_OBJECTS,
            }
        )
    with open(YAMCS_YAML, "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    print(f"Wrote {len(bucket_names)} image buckets to {YAMCS_YAML}")
