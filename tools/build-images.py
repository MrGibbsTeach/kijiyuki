#!/usr/bin/env python3
"""Build the responsive WebP set the site serves.

Usage:  python tools/build-images.py [source-dir]

Reads every .jpg/.png/.webp in source-dir (default: assets/img/_src) and
writes WebP variants into assets/img/w400, w800, w1400, w2000 and wmax.

- quality 80, Lanczos resampling
- never upscales: a step wider than the source is skipped
- wmax holds the source's own width (capped at 2000) whenever that width
  is not already one of the steps, so nothing is ever served below its
  native resolution

After adding photos, run this, then add the new paths to the <img> tags
(or to the IMAGES array in index.html for gallery shots). Each <img>
needs src, srcset, sizes, width, height.

Requires Pillow:  pip install Pillow
"""
import glob
import json
import os
import sys
import time

from PIL import Image

STEPS = [400, 800, 1400, 2000]
CAP = 2000
QUALITY = 80


def build(src_dir):
    srcs = sorted(
        f.replace(chr(92), '/')
        for pat in ('*.jpg', '*.jpeg', '*.png', '*.webp')
        for f in glob.glob(os.path.join(src_dir, pat))
    )
    if not srcs:
        sys.exit('no images found in %s' % src_dir)

    manifest = {}
    made = total = 0
    t0 = time.time()

    for f in srcs:
        name = os.path.splitext(os.path.basename(f))[0]
        with Image.open(f) as im:
            im = im.convert('RGB')
            w, h = im.size
            native = min(w, CAP)

            targets = {st: 'w%d' % st for st in STEPS if st <= w}
            if not targets:
                targets[w] = 'w400'
            targets.setdefault(native, 'wmax')

            manifest[name] = {'orig': [w, h], 'variants': {}}
            for tw, d in sorted(targets.items()):
                out_dir = os.path.join('assets', 'img', d)
                os.makedirs(out_dir, exist_ok=True)
                out = os.path.join(out_dir, name + '.webp').replace(chr(92), '/')
                im.resize((tw, max(1, round(h * tw / w))), Image.LANCZOS).save(
                    out, 'WEBP', quality=QUALITY, method=6)
                sz = os.path.getsize(out)
                made += 1
                total += sz
                manifest[name]['variants'][tw] = {
                    'path': out, 'w': tw, 'h': max(1, round(h * tw / w)), 'bytes': sz}

    with open('.img-manifest.json', 'w') as fh:
        json.dump(manifest, fh, indent=1)

    print('%d sources -> %d webp files in %.0fs, %.1f MB'
          % (len(srcs), made, time.time() - t0, total / 1048576))
    short = [n for n, d in manifest.items()
             if max(d['variants']) < min(d['orig'][0], CAP)]
    print('served below native width:', short or 'none')


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join('assets', 'img', '_src'))
