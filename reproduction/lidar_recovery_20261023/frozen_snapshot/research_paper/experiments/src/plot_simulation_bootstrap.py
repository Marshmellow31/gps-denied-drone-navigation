"""Raw simulation timeline; no thresholds or recovery labels."""
import argparse
import csv
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def read(path):
    with path.open(newline='') as stream: return list(csv.DictReader(stream))


def render(corridor, control, output):
    runs = [corridor, control]
    data = [(read(run / 'health.csv'), read(run / 'evaluation.csv')) for run in runs]
    times = [(int(row['timestamp_ns']) - 1000000000000) / 1e9
             for health, errors in data for row in health + errors]
    duration = max(4., math.ceil(max(times) / 4.) * 4.)
    image = Image.new('RGB', (1200, 940), 'white')
    draw = ImageDraw.Draw(image)
    path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(path, 16); title = ImageFont.truetype(path, 24)
    draw.text((55, 18), '40-second pilot: same motion, different geometric clues', fill='black', font=title)
    draw.text((55, 55), 'Teal: corridor. Purple: added-feature control. Gold: body inside corridor, not a recovery label.', fill='black', font=font)
    specs = [('Smallest online information eigenvalue (3 m lever scale)', 'eigenvalue_0', 'valid', True),
             ('Local translation error (m; 1 s window)', 'local_translation_error_m', 'local_valid', False),
             ('Local rotation error (radians; 1 s window)', 'local_rotation_error_rad', 'local_valid', False),
             ('Translation error after one fixed alignment at 5 s (m)', 'accumulated_translation_error_m', 'alignment_valid', False)]
    for panel, (label, key, valid, is_health) in enumerate(specs):
        selected = [[r for r in (h if is_health else e)
                     if (r['lever_scale_m'] == '3' if is_health else r['window_s'] == '1.0')]
                    for h, e in data]
        values = [float(r[key]) for rows in selected for r in rows if r[valid] == 'true']
        high = max(values) * 1.03 if max(values) > 0 else 1.
        top = 125 + 180 * panel; bottom = top + 125
        x = lambda t: 100 + t / duration * 1040
        y = lambda v: bottom - v / high * 125
        draw.text((55, top - 30), label, fill='black', font=font)
        draw.rectangle((x(9.25), top, x(24.25), bottom), fill='#fff2cc')
        for tick in range(0, int(duration) + 1, 4):
            draw.line((x(tick), top, x(tick), bottom), fill='#dddddd')
            draw.text((x(tick) - 8, bottom + 5), str(tick), fill='black', font=font)
        draw.text((8, top), f'{high:.3g}', fill='black', font=font)
        draw.text((8, bottom - 16), '0', fill='black', font=font)
        draw.rectangle((100, top, 1140, bottom), outline='#999999')
        for rows, color in zip(selected, ('#007175', '#884488')):
            previous = None
            for row in rows:
                if row[valid] != 'true': previous = None; continue
                t = (int(row['timestamp_ns']) - 1000000000000) / 1e9
                point = (x(t), y(float(row[key])))
                if previous is not None and t - previous[0] < .21:
                    draw.line((previous[1], point), fill=color, width=2)
                previous = (t, point)
    draw.text((480, 835), 'Seconds since first simulated scan', fill='black', font=font)
    draw.text((55, 880), 'One seeded development pair; synthetic truth. Seeded bias settings are stress values, not calibration.', fill='black', font=font)
    draw.text((55, 908), 'The geometry is simplified. Seeing a corridor does not by itself prove a fully unobservable direction.', fill='black', font=font)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--corridor', type=Path, required=True)
    parser.add_argument('--control', type=Path, required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    render(args.corridor, args.control, args.output)
