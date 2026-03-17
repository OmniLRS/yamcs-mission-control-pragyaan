import os
import time
from yamcs.client import YamcsClient
from util_images import create_background_image, save_image, publish_image_metadata

# Configuration constants
YAMCS_HOST = "localhost:8090"
YAMCS_INSTANCE = "workshop"
YAMCS_PROCESSOR = "realtime"
IMG_DIR = "/tmp/images_streaming"
WIDTH = 320
HEIGHT = 240
FONT_SIZE = HEIGHT // 20
SLEEP_INTERVAL = 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_IMG = os.path.join(SCRIPT_DIR, 'NavCam_low.png')

client = YamcsClient(YAMCS_HOST)
processor = client.get_processor(instance=YAMCS_INSTANCE, processor=YAMCS_PROCESSOR)

os.makedirs(IMG_DIR, exist_ok=True)

n = 1
while True:
    img = create_background_image(BACKGROUND_IMG, WIDTH, HEIGHT)
    text = f"Low Resolution Streaming Image {n:04d}"
    image_name = f"image_streaming_{n:04d}.png"
    save_image(img, text, FONT_SIZE, WIDTH, HEIGHT, IMG_DIR, image_name)
    publish_image_metadata(processor, YAMCS_HOST, "/Rover/camera/images_streaming", "images_streaming", n, image_name)

    n += 1
    time.sleep(SLEEP_INTERVAL)