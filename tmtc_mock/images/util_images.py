import io
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Cameras, buckets and MDB paths come from OmniLRS ($OMNILRS_ROOT), like the MDB generators.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "mdb"))
from _omnilrs import load_cameras, load_kind_resolution, load_naming, load_yamcs_tmtc, omnilrs_root  # noqa: E402


def load_omnilrs():
    """yamcs_naming module, robot cameras, controller yamcs_tmtc section and image kind -> resolution key of the
    OmniLRS checkout."""
    root = omnilrs_root()
    naming = load_naming(root)
    return naming, load_cameras(root), load_yamcs_tmtc(root), load_kind_resolution(root)


def image_size(cameras, kind_resolution, camera_name, kind):
    """(width, height) at which OmniLRS snaps that kind of image of the camera."""
    camera = next(cam for cam in cameras if cam.name == camera_name)
    return camera.resolutions[kind_resolution[kind]]


def create_background_image(image_path, width, height):
    return Image.open(image_path).convert('RGB').resize((width, height))


def _draw_text(draw, text, font, width, height, fill='black', position='center'):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if position == "center":
        x = (width - text_width) // 2
        y = (height - text_height) // 2
    elif position == "top-right":
        margin = 40
        x = width - text_width - margin
        y = margin
    else:
        x, y = position

    draw.text((x, y), text, fill=fill, font=font)


def create_depth_image(width, height):
    img_array = np.zeros((height, width, 4), dtype=np.uint8)
    for y in range(height):
        img_array[y, :, 3] = int((y / (height - 1)) * 255)
    return Image.fromarray(img_array, 'RGBA')


def upload_image(storage, img, text, font_size, width, height, bucket, image_name, fill='black', position='center'):
    """Draw `text` on the image and upload it as a PNG to the Yamcs storage bucket."""
    font = ImageFont.load_default(font_size)
    draw = ImageDraw.Draw(img)
    _draw_text(draw, text, font, width, height, fill, position)
    png = io.BytesIO()
    img.save(png, format="PNG")
    png.seek(0)
    storage.upload_object(bucket, image_name, png, content_type="image/png")
    print(f"Uploaded {bucket}/{image_name}")


def publish_image_metadata(processor, yamcs_host, meta_path, bucket, count, image_name):
    url_storage = f"/storage/buckets/{bucket}/objects/{image_name}"
    url_full = f"http://{yamcs_host}/api{url_storage}"
    processor.set_parameter_values({
        f"{meta_path}/number": count,
        f"{meta_path}/name": image_name,
        f"{meta_path}/url_storage": url_storage,
        f"{meta_path}/url_full": url_full,
    })
    return url_storage, url_full
