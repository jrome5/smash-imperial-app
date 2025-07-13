#a seperate visualisations script with minimal dependencies

from PIL import Image, ImageDraw, ImageOps
import numpy as np
import os
from character_roster import roster

ICON_SIZE = (64, 64)

def load_character_icon(character):
    if character == "blank":
        return Image.new("RGB", ICON_SIZE, color=(255, 255, 255))  # white blank

    filename = f"{character}.png"
    path = os.path.join("Stock Icons", filename)

    try:
        img = Image.open(path).convert("RGBA").resize(ICON_SIZE)
    except Exception:
        return Image.new("RGB", ICON_SIZE, color=(255, 255, 255))

    # Extract RGB and alpha
    rgb = img.convert("RGB")
    alpha = img.getchannel("A")

    # Calculate average RGB over visible (non-transparent) area
    arr_rgb = np.array(rgb).astype(np.float32) / 255
    arr_alpha = np.array(alpha).astype(np.float32) / 255
    mean_rgb = np.sum(arr_rgb * arr_alpha[..., None], axis=(0, 1)) / (np.sum(arr_alpha) + 1e-5)
    comp_rgb = 1.0 - mean_rgb
    comp_color = tuple((comp_rgb * 255).astype(np.uint8))

    # Composite over background
    bg = Image.new("RGB", ICON_SIZE, color=comp_color)
    out = Image.alpha_composite(bg.convert("RGBA"), img)
    return out.convert("RGB")

def add_transparent_rectangle(img: Image.Image, color=(255, 0, 0), alpha=0.4):
    overlay = Image.new("RGB", ICON_SIZE, color=color)
    blended = Image.blend(img, overlay, alpha)
    return blended

def plot_map(map=None, save=False, map_count=0, return_image=False, attacker=None, defender=None):
    if map is None:
        map = roster

    grid_images = []
    for row in map:
        row_images = []
        for char in row:
            icon = load_character_icon(char)
            if char == attacker:
                icon = add_transparent_rectangle(icon, color=(255, 0, 0))  # red
            elif char == defender:
                icon = add_transparent_rectangle(icon, color=(0, 0, 255))  # blue
            row_images.append(icon)
        grid_images.append(row_images)

    # Combine the rows into one final image
    rows_combined = [Image.fromarray(np.hstack([np.array(img) for img in row])) for row in grid_images]
    final_img = Image.fromarray(np.vstack([np.array(row) for row in rows_combined]))

    if save:
        if not os.path.exists("Maps"):
            os.makedirs("Maps")
        filename = f"Maps/map{map_count:03}.png"
        final_img.save(filename)

    if return_image:
        return final_img