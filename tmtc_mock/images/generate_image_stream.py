import os
import time
from yamcs.client import YamcsClient
from util_images import create_background_image, load_omnilrs, upload_image, publish_image_metadata

# Configuration constants
YAMCS_HOST = "localhost:8090"
YAMCS_INSTANCE = "workshop"
YAMCS_PROCESSOR = "realtime"
WIDTH = 320
HEIGHT = 240
FONT_SIZE = HEIGHT // 20
SLEEP_INTERVAL = 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_IMG = os.path.join(SCRIPT_DIR, 'NavCam_low.png')

naming, cameras, _ = load_omnilrs()
streaming_cameras = [cam["name"] for cam in cameras if naming.has_type(cam, "rgba")]

client = YamcsClient(YAMCS_HOST)
processor = client.get_processor(instance=YAMCS_INSTANCE, processor=YAMCS_PROCESSOR)
storage = client.get_storage_client()  # the image buckets are declared in yamcs.yaml (mdb/generate_mdb_rover.py)

n = 1
while True:
    for camera in streaming_cameras:
        bucket = naming.bucket_name(camera, "streaming")
        img = create_background_image(BACKGROUND_IMG, WIDTH, HEIGHT)
        text = f"{camera} Low Res Streaming Image {n:04d}"
        image_name = f"image_streaming_{n:04d}.png"
        upload_image(storage, img, text, FONT_SIZE, WIDTH, HEIGHT, bucket, image_name)
        publish_image_metadata(processor, YAMCS_HOST, naming.meta_path(camera, "streaming"), bucket, n, image_name)

    n += 1
    time.sleep(SLEEP_INTERVAL)
