import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


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


def save_image(img, text, font_size, width, height, directory, image_name, fill='black', position='center'):
    font = ImageFont.load_default(font_size)
    draw = ImageDraw.Draw(img)
    _draw_text(draw, text, font, width, height, fill, position)
    img_path = os.path.join(directory, image_name)
    img.save(img_path)
    print(f"Saved {img_path}")
    return img_path


def publish_image_metadata(processor, yamcs_host, base_path, bucket, count, image_name):
    url_storage = f"/storage/buckets/{bucket}/objects/{image_name}"
    url_full = f"http://{yamcs_host}/api{url_storage}"
    processor.set_parameter_values({
        f"{base_path}/number": count,
        f"{base_path}/name": image_name,
        f"{base_path}/url_storage": url_storage,
        f"{base_path}/url_full": url_full,
    })
    return url_storage, url_full
