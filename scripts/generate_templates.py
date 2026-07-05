import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(HERE, "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1080, 1350

CREAM_TOP = (247, 238, 222)
CREAM_BOTTOM = (235, 221, 196)
DARK_TOP = (43, 28, 20)
ORANGE_BOTTOM = (200, 116, 46)


def vertical_gradient(w, h, top, bottom):
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / (h - 1)
        arr[y, :, 0] = int(top[0] + (bottom[0] - top[0]) * t)
        arr[y, :, 1] = int(top[1] + (bottom[1] - top[1]) * t)
        arr[y, :, 2] = int(top[2] + (bottom[2] - top[2]) * t)
    return Image.fromarray(arr, "RGB")


def add_grain(img_rgb, amount=5):
    arr = np.array(img_rgb).astype(np.int16)
    noise = np.random.randint(-amount, amount + 1, arr.shape[:2] + (1,))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def add_vignette(img_rgb, strength=60):
    w, h = img_rgb.size
    cx, cy = w / 2, h / 2
    y, x = np.ogrid[:h, :w]
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    norm = np.clip(dist / max_dist, 0, 1)
    darkness = (norm ** 2) * strength
    arr = np.array(img_rgb).astype(np.int16)
    arr = np.clip(arr - darkness[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def make_cream_template(filename):
    img = vertical_gradient(W, H, CREAM_TOP, CREAM_BOTTOM)
    img = add_grain(img, amount=4)
    img = add_vignette(img, strength=40)
    draw = ImageDraw.Draw(img)
    margin = 60
    draw.line([(margin, 130), (W - margin, 130)], fill=(178, 128, 74, 255), width=2)
    draw.line([(margin, H - 110), (W - margin, H - 110)], fill=(178, 128, 74, 255), width=2)
    img.save(os.path.join(ASSETS_DIR, filename))


def make_dark_template(filename):
    img = vertical_gradient(W, H, DARK_TOP, ORANGE_BOTTOM)
    img = add_grain(img, amount=5)
    img = add_vignette(img, strength=70)
    img.save(os.path.join(ASSETS_DIR, filename))


if __name__ == "__main__":
    make_cream_template("template_cream.png")
    make_dark_template("template_dark.png")
    print("OK: template_cream.png + template_dark.png gerados em", ASSETS_DIR)
