"""Plot a development-only diagnostic/error timeline; never infer recovery."""
import argparse
import csv
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ORIGIN_NS = 1649856227623466000


def render(health_path, evaluation_path, output):
    with open(health_path, newline="") as stream:
        health = [r for r in csv.DictReader(stream) if r['lever_scale_m'] == '3']
    with open(evaluation_path, newline="") as stream:
        errors = list(csv.DictReader(stream))
    image = Image.new('RGB', (1200, 980), 'white')
    draw = ImageDraw.Draw(image)
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 16)
    title = ImageFont.truetype(font_path, 23)
    draw.text((60, 18), 'Development pilot: more geometric clues are not proof of recovery', fill='black', font=title)
    draw.text((60, 54), 'Gold = scene exit (31.6–33.6 s). Grey = unavailable. No recovery threshold or label.', fill='black', font=font)
    specs = [
        ('Measurement-only information: smallest eigenvalue (log10; lever scale 3 m)',
         health, 'eigenvalue_0', 'valid', lambda v: math.log10(max(v, 1e-12))),
        ('Local translation error (m; 1 s window)', [r for r in errors if r['window_s'] == '1.0'],
         'local_translation_error_m', 'local_valid', float),
        ('Local rotation error (degrees; 1 s window)', [r for r in errors if r['window_s'] == '1.0'],
         'local_rotation_error_rad', 'local_valid', lambda v: math.degrees(float(v))),
        ('Translation error after ONE fixed pre-exit alignment (m)',
         [r for r in errors if r['window_s'] == '1.0'],
         'accumulated_translation_error_m', 'alignment_valid', float),
    ]
    for panel, (label, rows, value_key, valid_key, transform) in enumerate(specs):
        top = 125 + panel * 190
        bottom = top + 130
        values = [transform(float(r[value_key])) for r in rows if r[valid_key] == 'true']
        low = min(0, min(values)); high = max(values)
        if high <= low: high = low + 1
        x = lambda t: 100 + t / 55 * 1040
        y = lambda v: bottom - (v - low) / (high - low) * 130
        draw.text((60, top - 30), label, fill='black', font=font)
        draw.rectangle((x(31.6), top, x(33.6), bottom), fill='#ffefbc')
        for tick in range(0, 56, 5):
            draw.line((x(tick), top, x(tick), bottom), fill='#eeeeee')
            draw.text((x(tick) - 8, bottom + 5), str(tick), fill='black', font=font)
        draw.text((8, top), f'{high:.3g}', fill='black', font=font)
        draw.text((8, bottom - 16), f'{low:.3g}', fill='black', font=font)
        draw.rectangle((100, top, 1140, bottom), outline='#999999')
        previous = None
        for row in rows:
            t = (int(row['timestamp_ns']) - ORIGIN_NS) / 1e9
            if row[valid_key] != 'true':
                draw.line((x(t), top, x(t), bottom), fill='#dddddd')
                previous = None
                continue
            point = (x(t), y(transform(float(row[value_key]))))
            if previous is not None and t - previous[0] < .21:
                draw.line((previous[1], point), fill='#007175', width=2)
            previous = (t, point)
        if panel == 3:
            draw.text((500, bottom + 28), 'Seconds since first laser scan', fill='black', font=font)
    draw.text((60, 913), 'Post-exit: only 13/56 valid 1 s windows; 0/56 valid 3 s windows. Sustained recovery unproven.', fill='black', font=font)
    draw.text((60, 941), 'Hilti-Oxford Exp18, handheld; reference partly LiDAR-map-derived. Development only, no flight claim.', fill='black', font=font)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--health', required=True)
    parser.add_argument('--evaluation', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    render(args.health, args.evaluation, args.output)
