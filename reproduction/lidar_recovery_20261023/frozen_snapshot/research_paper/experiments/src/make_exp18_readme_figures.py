"""Build small, attributed README figures from the verified Exp18 development bag.

Requires rosbags 0.11.5, NumPy and Pillow. No estimator output influences the
scene snapshots or transition time. The timeline uses recorded coverage only.
"""

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore


INK = (28, 42, 56)
MUTED = (76, 92, 107)
TEAL = (0, 113, 117)
GOLD = (232, 170, 54)
PAPER = (250, 251, 252)


def font(size):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)


def choose_scans(bag):
    """Take the nearest LiDAR scans to +25 and +40 seconds, before errors exist."""
    types = get_typestore(Stores.ROS1_NOETIC)
    chosen = {}
    targets = (25.0, 40.0)
    with Reader(bag) as reader:
        conn = next(c for c in reader.connections if c.topic == "/hesai/pandar")
        start = reader.start_time
        for _, _, raw in reader.messages(connections=[conn]):
            msg = types.deserialize_ros1(raw, conn.msgtype)
            stamp = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
            relative = (stamp - start) / 1e9
            for target in targets:
                if target not in chosen or abs(relative - target) < abs(chosen[target][0] - target):
                    points = np.ndarray((msg.width * msg.height,), dtype=np.dtype({
                        "names": ["x", "y", "z"], "formats": ["<f4"] * 3,
                        "offsets": [0, 4, 8], "itemsize": msg.point_step,
                    }), buffer=msg.data)
                    chosen[target] = (relative, points.copy())
            if relative > max(targets) + 0.2:
                break
    return [chosen[target] for target in targets]


def scene_image(scans, output):
    image = Image.new("RGB", (1120, 660), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((40, 27), "What the laser saw", font=font(30), fill=INK)
    draw.text((40, 78), "View from above - both pictures show the same 30 m wide area", font=font(19), fill=MUTED)
    panel_size, panel_y = 450, 145
    for idx, (relative, points) in enumerate(scans):
        panel_x = 65 + idx * 540
        radius = 15.0
        x, y, z = points["x"], points["y"], points["z"]
        good = (np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
                & (np.abs(x) < radius) & (np.abs(y) < radius)
                & (z > -3) & (z < 3))
        hist, _, _ = np.histogram2d(y[good], x[good], bins=panel_size,
                                    range=[[-radius, radius], [-radius, radius]])
        intensity = np.minimum(220, np.log1p(hist) * 75)
        pixels = (255 - np.flipud(intensity)).astype(np.uint8)
        panel = Image.fromarray(pixels, "L").convert("RGB")
        image.paste(panel, (panel_x, panel_y))
        for metres in (-10, -5, 5, 10):
            coordinate = panel_x + int((metres + radius) / (2 * radius) * panel_size)
            draw.line((coordinate, panel_y, coordinate, panel_y + panel_size), fill=(226, 232, 236), width=1)
            horizontal = panel_y + int((radius - metres) / (2 * radius) * panel_size)
            draw.line((panel_x, horizontal, panel_x + panel_size, horizontal), fill=(226, 232, 236), width=1)
        centre = (panel_x + panel_size // 2, panel_y + panel_size // 2)
        draw.ellipse((centre[0]-5, centre[1]-5, centre[0]+5, centre[1]+5), fill=TEAL)
        draw.rectangle((panel_x, panel_y, panel_x + panel_size, panel_y + panel_size), outline=(180, 193, 202), width=2)
        ranges = np.sqrt(x.astype("f8")**2 + y.astype("f8")**2 + z.astype("f8")**2)
        p90 = float(np.percentile(ranges[np.isfinite(ranges)], 90))
        label = "Mostly nearby surfaces" if idx == 0 else "Distant structure becomes visible"
        draw.text((panel_x, 113), f"{label}  (+{relative:.1f} s)", font=font(19), fill=INK)
        draw.text((panel_x, 603), f"90% of returns within {p90:.1f} m", font=font(19), fill=INK)
    draw.text((40, 640), "Data: Hilti-Oxford 2022 (CC BY-NC-SA 3.0). Dark marks are LiDAR returns; blue dot is the sensor.",
              font=font(14), fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    print(output)


def timeline_image(reference_path, output):
    times = [float(line.split()[0]) for line in reference_path.read_text().splitlines() if line.strip()]
    origin = 1649856227.623466
    bag_end = 1649856336.918471 - origin
    gaps = [(a - origin, b - origin) for a, b in zip(times, times[1:]) if b - a > 0.5]
    image = Image.new("RGB", (1120, 475), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((42, 28), "How much of the recording we have checked", font=font(28), fill=INK)
    draw.text((42, 75), "Seconds since the first laser scan", font=font(18), fill=MUTED)
    left, right = 255, 1055
    scale = (right - left) / 110.0

    def xx(seconds):
        return left + round(seconds * scale)

    for tick in (0, 20, 40, 60, 80, 100, 110):
        x = xx(tick)
        draw.line((x, 118, x, 372), fill=(223, 229, 232), width=1)
        draw.text((x-10, 385), str(tick), font=font(16), fill=MUTED)
    rows = [("Laser + motion sensor", 145, bag_end, TEAL),
            ("Reference path", 225, times[-1]-origin, (90, 116, 158)),
            ("Our first trial", 305, 55.0, (68, 140, 94))]
    for label, y, end, color in rows:
        draw.text((42, y+4), label, font=font(18), fill=INK)
        draw.rounded_rectangle((left, y, xx(end), y+32), radius=6, fill=color)
    for gap_start, gap_end in gaps:
        draw.rectangle((xx(gap_start), 225, max(xx(gap_start)+2, xx(gap_end)), 257), fill=PAPER)
    draw.rectangle((xx(32), 128, xx(36), 355), fill=(245, 215, 153), outline=GOLD, width=1)
    draw.text((xx(32)-80, 104), "possible scene change", font=font(15), fill=INK)
    draw.text((xx(55)+6, 308), "55 s", font=font(16), fill=INK)
    draw.text((xx(times[-1]-origin)+6, 228), "86.7 s", font=font(16), fill=INK)
    draw.text((xx(bag_end)-64, 148), "109.3 s", font=font(16), fill=INK)
    draw.text((42, 422), "White cuts = larger reference gaps. Gold band = a possible change, not proven recovery.",
              font=font(16), fill=INK)
    draw.text((42, 450), "Data: Hilti-Oxford 2022 (CC BY-NC-SA 3.0). Trial: this project's FAST-LIO development run.",
              font=font(14), fill=MUTED)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, optimize=True)
    print(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    scene_image(choose_scans(args.bag), args.output_dir / "exp18_lidar_before_after.png")
    timeline_image(args.reference, args.output_dir / "exp18_data_timeline.png")


if __name__ == "__main__":
    main()
