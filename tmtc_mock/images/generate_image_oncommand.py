import os
import socket
from collections import defaultdict
from yamcs.client import YamcsClient
from util_images import create_background_image, create_depth_image, load_omnilrs, upload_image, publish_image_metadata

# Configuration constants
YAMCS_HOST = "localhost:8090"
YAMCS_INSTANCE = "workshop"
YAMCS_PROCESSOR = "realtime"
WIDTH = 1440
HEIGHT = 1080
FONT_SIZE = HEIGHT // 15
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKGROUND_IMG = os.path.join(SCRIPT_DIR, 'NavCam_high.png')
LANDER_BACKGROUND_IMG = os.path.join(SCRIPT_DIR, 'lander_cam.png')

# defined in yamcs-server/src/main/yamcs/etc/yamcs.workshop.yaml for the datalink with the "tc_realtime" stream
TC_RECEIVE_ADDRESS = '127.0.0.1'
TC_RECEIVE_PORT    = 10025

# Cameras and buckets from OmniLRS: robot cameras via yamcs_naming, lander and APXS buckets from the controller yaml
naming, cameras, yamcs_tmtc = load_omnilrs()
LANDER_BUCKET = yamcs_tmtc["images"]["buckets"]["lander"]
APXS_BUCKET = yamcs_tmtc["payload"]["apxs"]["bucket"]


def detect_command(data):
    for cmd_name in [
        b'camera_capture_high',
        b'camera_streaming',
        b'camera_capture_depth',
        b'lander_camera_capture',
        b'payload_capture_apxs',
    ]:
        if data.startswith(cmd_name):
            return cmd_name, len(cmd_name)
    return None, 0


def camera_arg(cmd_name, data, cmd_name_len):
    """Camera selected by the camera_name argument (first byte after the command name)."""
    return naming.cameras_for_command(cameras, cmd_name.decode())[data[cmd_name_len]]


def seed_apxs_image(processor, storage):
    """Create and publish a default APXS image for sequence 0."""
    image_name = "image_apxs_0000.png"
    apxs_background = os.path.join(SCRIPT_DIR, 'APXS_nodata.png')
    upload_image(
        storage,
        create_background_image(apxs_background, WIDTH, HEIGHT),
        " ", FONT_SIZE, WIDTH, HEIGHT,
        APXS_BUCKET["name"], image_name,
        position='top-right',
    )
    publish_image_metadata(processor, YAMCS_HOST, APXS_BUCKET["path"], APXS_BUCKET["name"], 0, image_name)


def handle_command(processor, storage, command_counts, cmd_name, cmd_name_len, data):
    if cmd_name == b'camera_capture_high' and len(data) == cmd_name_len + 1:
        camera = camera_arg(cmd_name, data, cmd_name_len)
        print(f'Received: camera_capture_high {camera}')
        command_counts[(camera, "oncommand")] += 1
        seq = command_counts[(camera, "oncommand")]
        text = f"{camera} High Resolution OnCommand Image {seq:04d}"
        image_name = f"image_oncommand_{seq:04d}.png"
        bucket = naming.bucket_name(camera, "oncommand")
        upload_image(storage, create_background_image(BACKGROUND_IMG, WIDTH, HEIGHT), text, FONT_SIZE, WIDTH, HEIGHT, bucket, image_name)
        publish_image_metadata(processor, YAMCS_HOST, naming.meta_path(camera, "oncommand"), bucket, seq, image_name)

    elif cmd_name == b'camera_streaming':
        if len(data) == cmd_name_len + 2:
            camera = camera_arg(cmd_name, data, cmd_name_len)
            action = "START" if data[cmd_name_len + 1] == 1 else "STOP"
            print(f'Received: camera_streaming {camera} {action}')
        else:
            print(f'Error: camera_streaming command has {len(data)} bytes, expected {cmd_name_len + 2}')

    elif cmd_name == b'camera_capture_depth' and len(data) == cmd_name_len + 1:
        camera = camera_arg(cmd_name, data, cmd_name_len)
        print(f'Received: camera_capture_depth {camera}')
        command_counts[(camera, "depth")] += 1
        seq = command_counts[(camera, "depth")]
        text = f"{camera} Depth OnCommand Image {seq:04d}"
        image_name = f"image_depth_{seq:04d}.png"
        bucket = naming.bucket_name(camera, "depth")
        upload_image(storage, create_depth_image(WIDTH, HEIGHT), text, FONT_SIZE, WIDTH, HEIGHT, bucket, image_name, fill=(0, 0, 0, 255))
        publish_image_metadata(processor, YAMCS_HOST, naming.meta_path(camera, "depth"), bucket, seq, image_name)

    elif cmd_name == b'lander_camera_capture' and len(data) == cmd_name_len:
        print('Received: lander_camera_capture')
        command_counts["lander_high"] += 1
        seq = command_counts["lander_high"]
        text = f"Lander OnCommand Image {seq:04d}"
        image_name = f"lander_image_oncommand_{seq:04d}.png"
        upload_image(storage, create_background_image(LANDER_BACKGROUND_IMG, WIDTH, HEIGHT), text, FONT_SIZE, WIDTH, HEIGHT, LANDER_BUCKET["name"], image_name)
        publish_image_metadata(processor, YAMCS_HOST, LANDER_BUCKET["path"], LANDER_BUCKET["name"], seq, image_name)

    elif cmd_name == b'payload_capture_apxs' and len(data) == cmd_name_len:
        print('Received: payload_capture_apxs')
        command_counts["rover_apxs"] += 1
        seq = command_counts["rover_apxs"]
        text = f"{seq}"
        image_name = f"image_apxs_{seq:04d}.png"
        apxs_background = os.path.join(SCRIPT_DIR, 'APXS_measurement.png')
        upload_image(
            storage,
            create_background_image(apxs_background, WIDTH, HEIGHT),
            text, FONT_SIZE, WIDTH, HEIGHT,
            APXS_BUCKET["name"], image_name,
            position='top-right',
        )
        publish_image_metadata(processor, YAMCS_HOST, APXS_BUCKET["path"], APXS_BUCKET["name"], seq, image_name)

    else:
        print(f"Unknown command: {len(data)} bytes, hex: {data.hex()}")


def main():
    client = YamcsClient(YAMCS_HOST)
    processor = client.get_processor(instance=YAMCS_INSTANCE, processor=YAMCS_PROCESSOR)
    storage = client.get_storage_client()  # the image buckets are declared in yamcs.yaml (mdb/generate_mdb_rover.py)

    tc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tc_socket.bind((TC_RECEIVE_ADDRESS, TC_RECEIVE_PORT))

    command_counts = defaultdict(int)

    seed_apxs_image(processor, storage)

    print(f"Listening for commands on UDP {TC_RECEIVE_ADDRESS}:{TC_RECEIVE_PORT}...")
    while True:
        data, _ = tc_socket.recvfrom(4096)
        cmd_name, cmd_name_len = detect_command(data)
        handle_command(processor, storage, command_counts, cmd_name, cmd_name_len, data)


if __name__ == "__main__":
    main()
