import os
import time
from yamcs.client import YamcsClient
from util_images import create_background_image, image_size, load_omnilrs, upload_image, publish_image_metadata

# Configuration constants
YAMCS_HOST = "localhost:8090"
YAMCS_INSTANCE = "workshop"
YAMCS_PROCESSOR = "realtime"
SLEEP_INTERVAL = 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_IMG = os.path.join(SCRIPT_DIR, 'NavCam_low.png')

naming, cameras, _, kind_resolution = load_omnilrs()  # images at the resolution OmniLRS streams at
streaming_cameras = [cam.name for cam in cameras if cam.has_type("rgba")]

client = YamcsClient(YAMCS_HOST)
processor = client.get_processor(instance=YAMCS_INSTANCE, processor=YAMCS_PROCESSOR)
storage = client.get_storage_client()  # the image buckets are declared in yamcs.yaml (mdb/generate_mdb_rover.py)

n = 1
while True:
    for camera in streaming_cameras:
        bucket = naming.bucket_name(camera, "streaming")
        width, height = image_size(cameras, kind_resolution, camera, "streaming")
        img = create_background_image(BACKGROUND_IMG, width, height)
        text = f"{camera} Low Res Streaming Image {n:04d}"
        image_name = f"image_streaming_{n:04d}.png"
        upload_image(storage, img, text, height // 20, width, height, bucket, image_name)
        publish_image_metadata(processor, YAMCS_HOST, naming.meta_path(camera, "streaming"), bucket, n, image_name)

    n += 1
    time.sleep(SLEEP_INTERVAL)
