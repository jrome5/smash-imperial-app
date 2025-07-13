import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
from character_roster import roster
import cv2
import numpy as np
import os
def load_character_icon(character):
    if character == "blank":
        return np.zeros((64, 64, 3), dtype=np.uint8)

    filename = f"{character}.png"
    path = "Stock Icons/" + filename
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # Load as RGBA

    if img is None or img.shape[2] != 4:
        return np.zeros((64, 64, 3), dtype=np.uint8)

    rgba = img.astype(np.float32) / 255.0
    rgb = rgba[..., :3]
    alpha = rgba[..., 3:]

    # Compute average visible RGB color
    mean_rgb = np.sum(rgb * alpha, axis=(0, 1)) / (np.sum(alpha) + 1e-5)
    comp_rgb = 1.0 - mean_rgb  # Complement color

    # Create background with complementary color
    bg = np.ones_like(rgb) * comp_rgb

    # Alpha blend: result = alpha * fg + (1 - alpha) * bg
    blended = alpha * rgb + (1 - alpha) * bg
    blended = (blended * 255).astype(np.uint8)

    # Convert to BGR for OpenCV
    blended = cv2.cvtColor(blended, cv2.COLOR_RGB2BGR)
    return blended

def add_transparent_rectangle(img, color):
    # Initialize blank mask image of same dimensions for drawing the shapes
    shapes = np.zeros_like(img, np.uint8)

    # Draw shapes
    cv2.rectangle(shapes, (0, 0), (64, 64), color, cv2.FILLED)

    # Generate output by blending image with shapes image, using the shapes
    # images also as mask to limit the blending to those parts
    out = img.copy()
    alpha = 0.5
    mask = shapes.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, shapes, 1 - alpha, 0)[mask]
    return out

def plot_map(map=None, save=False, map_count=0, show=False, return_image=False, attacker=None, defender=None):
    imgs = []
    if map is None:
        map = roster
    for line in map:
        imgs_line = []
        for character in line:
            img = load_character_icon(character)
            if character == attacker:
                img = add_transparent_rectangle(img, (255, 0, 0))
                # cv2.rectangle(img, (0, 0), (64, 64), (255, 0, 0), -1)  # Red border
            if character == defender:
                img = add_transparent_rectangle(img, (0, 0, 255))
                # cv2.rectangle(img, (0, 0), (64, 64), (0, 0, 255), -1)  # Blue border
            imgs_line.append(img)
        imgs.append(np.concatenate(imgs_line, axis=1))

    img = np.concatenate(imgs, axis=0)
    # print(img.shape)
    if save:
        if not os.path.exists("Maps"):
            os.makedirs("Maps")
        if map_count < 10:
            map_count = f"00{map_count}"
        elif map_count < 100:
            map_count = f"0{map_count}"
        cv2.imwrite(f"Maps/map{map_count}.png", img)
    if show:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.figure(figsize=(10, 10))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
    if return_image:
        return img
    # return img

def plot_map_animation():
    folder = "Maps"
    images = []

    # Load images in sorted order
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            filepath = os.path.join(folder, filename)
            img = cv2.imread(filepath)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                images.append(img_rgb)

    # Display with a single figure and axis
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 10))
    img_display = ax.imshow(images[0])
    ax.axis('off')

    for img in images:
        img_display.set_data(img)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.2)

    plt.ioff()
    plt.show()

from matplotlib.animation import FFMpegWriter

def plot_map_animation_to_mp4(output_file="map_animation_cv2.mp4", fps=10):
    folder = "Maps"
    images = []

    # Load and convert all images
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".png"):
            print(filename)
            filepath = os.path.join(folder, filename)
            img = cv2.imread(filepath)
            if img is not None:
                images.append(img)

    if not images:
        print("No images found.")
        return

    height, width, _ = images[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    for img in images:
        resized_img = cv2.resize(img, (width, height))  # Ensure consistent size
        writer.write(resized_img)

    writer.release()
    print(f"Video saved to: {output_file}")