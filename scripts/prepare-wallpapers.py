"""Prepare supplied originals in ignored staging; never replace app assets automatically.

The Shanghai set uses Pillow (development dependency only); see docs/assets.md.
Each photo also gets a 3840 x 2160 crop for the 4K video-layer wallpaper.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '.local/materials/wallpapers'
PHOTOS = [
    ('bund', 'The Bund at blue hour', 'bund.jpg', 'Li Yang', '5h_dMuX_7RE', 'dark'),
    ('mirror', 'Lujiazui reflections', 'mirror.jpg', 'Freeman Zhou', 'oV9hp8wXkPE', 'dark'),
    ('hongkou', 'Night from Hongkou', 'hongkou.jpg', '鱼 鱼', '9CFR4gROdcs', 'dark'),
    ('waibaidu', 'Waibaidu Bridge', 'waibaidu.jpg', 'Richard Liu', 'AhC3Zdn5wOQ', 'light'),
    ('huangpu', 'Huangpu at night', 'huangpu.jpg', 'Ilan Michel', 'GeC2q7JzpQU', 'dark'),
    ('zhongshan', 'Zhongshan Road lights', 'zhongshan.jpg', 'Kounotori', 'IU_nBd0oYPA', 'dark'),
    ('reflection', 'River glow', 'reflection.jpg', 'Henry Chen', 'Is3SdpT7OA4', 'dark'),
    ('sunset', 'Pudong sunset', 'sunset.jpg', 'ZENG YILI', 'NFMbwZHT6vE', 'light'),
    ('waterfront', 'Blue waterfront', 'waterfront.jpg', 'Henry Chen', 'ZEVe7PyDBs4', 'dark'),
    ('silhouette', 'Skyline silhouette', 'silhouette.jpg', 'Pen Tsai', 'djByJFHwFbY', 'dark'),
    ('customs', 'Custom House clock', 'customs.jpg', 'Archcookie', 'gk-Gfo1cx1k', 'dark'),
    ('dusk', 'Golden dusk', 'dusk.jpg', 'Lewis BD', 'pGk6UjPYjxQ', 'light'),
    ('skyline', 'Towers at dusk', 'skyline.jpg', 'Lijian (Richard) Zhu', 'sze3ar5-Isw', 'dark'),
    ('heritage', 'Bund heritage', 'heritage.jpg', 'Lijian (Richard) Zhu', 'xA8Rc6IgWUk', 'dark'),
    ('daylight', 'Huangpu daylight', 'daylight.jpg', 'Rich Xu', 'oqOQ9D4Q08E', 'light'),
    # Second selection, 27 October 2026; two are from New York and Tokyo.
    ('tower', 'Shanghai Tower aerial', 'tower.jpg', 'Zhou Xian', '7tFFO6Mq5L4', 'dark'),
    ('teal', 'Teal tower sprawl', 'teal.jpg', 'Himmel S', 'ZyC_qGWPZiM', 'dark'),
    ('pearl', 'Pearl Tower alone', 'pearl.jpg', 'Cici Hung', 'QR9SZy396rg', 'dark'),
    ('riverbend', 'Huangpu river bend', 'riverbend.jpg', 'Oliver Wilson', '8KV6W31hVzU', 'dark'),
    ('brooklyn', 'Brooklyn Bridge', 'brooklyn.jpg', 'Jonathan Pease', '1nlhZy86uPU', 'dark'),
    ('aerial', 'Golden hour aerial', 'aerial.jpg', 'Denys Nevozhai', 'D8iZPlX-2fs', 'dark'),
    ('pearlsunset', 'Pearl Tower sunset', 'pearlsunset.jpg', 'Yifan Cong', 'GszVE92a5Rs', 'dark'),
    ('haze', 'Hazy river aerial', 'haze.jpg', 'Road Trip with Raj', 'py8eyAh9J3A', 'light'),
    ('fuji', 'Tokyo Tower and Fuji', 'fuji.jpg', 'Clement Souchet', 'FVK-lpEc-Bc', 'light'),
]
# Every Shanghai photo uses the Pillow cover recipe; originals are 3840px Unsplash renditions.
COVER_IDS = {photo[0] for photo in PHOTOS}


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def prepare_legacy(path, id):
    # Keep the reviewed nine-photo recipe unchanged, including aspect ratio.
    for tag, width, quality in [('', 1920, 87), ('-thumb', 512, 80)]:
        subprocess.run([
            'sips', '-Z', str(width), '-s', 'format', 'jpeg',
            '-s', 'formatOptions', str(quality), str(path),
            '--out', str(OUTPUT / (id + tag + '.jpg')),
        ], check=True, capture_output=True)


def prepare_cover(path, id, Image, ImageOps):
    with Image.open(path) as original:
        original.load()
        profile = original.info.get('icc_profile')
        image = ImageOps.exif_transpose(original).convert('RGB')
    uhd = ImageOps.fit(image, (3840, 2160), Image.Resampling.LANCZOS,
                       centering=(0.5, 0.5))
    uhd.save(OUTPUT / (id + '-4k.jpg'), 'JPEG', quality=94, subsampling=0,
             optimize=True, icc_profile=profile)
    background = uhd.resize((1920, 1080), Image.Resampling.LANCZOS)
    thumbnail = background.resize((512, 288), Image.Resampling.LANCZOS)
    for tag, image, quality, subsampling in [
        ('', background, 90, 0), ('-thumb', thumbnail, 85, 2),
    ]:
        image.save(OUTPUT / (id + tag + '.jpg'), 'JPEG', quality=quality,
                   subsampling=subsampling, optimize=True, progressive=False,
                   icc_profile=profile)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path,
                        help='Folder containing the selected original Unsplash filenames')
    parser.add_argument('--ids', help='Comma-separated wallpaper IDs; default: all')
    args = parser.parse_args()
    requested = None if args.ids is None else {id.strip() for id in args.ids.split(',')}
    known = {photo[0] for photo in PHOTOS}
    if requested is not None and ('' in requested or requested - known):
        parser.error('--ids must contain these IDs: ' + ', '.join(photo[0] for photo in PHOTOS))
    selected = [photo for photo in PHOTOS if requested is None or photo[0] in requested]
    paths = {photo[0]: args.source / photo[2]
             for photo in selected}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        parser.error('Missing selected originals:\n' + '\n'.join(missing))
    if any(photo[0] not in COVER_IDS for photo in selected) and not shutil.which('sips'):
        parser.error('The original nine-photo recipe requires macOS sips.')
    Image = ImageOps = None
    if any(photo[0] in COVER_IDS for photo in selected):
        try:
            from PIL import Image, ImageOps
        except ImportError:
            parser.error('The Shanghai photos require Pillow. See docs/assets.md.')

    OUTPUT.mkdir(parents=True, exist_ok=True)
    items = []
    for id, name, filename, credit, source, tone in selected:
        path = paths[id]
        original_hash = file_hash(path)
        if id in COVER_IDS:
            prepare_cover(path, id, Image, ImageOps)
        else:
            prepare_legacy(path, id)
        if file_hash(path) != original_hash:
            raise RuntimeError('Original changed while preparing: ' + str(path))
        background, thumbnail = OUTPUT / (id + '.jpg'), OUTPUT / (id + '-thumb.jpg')
        items.append(dict(
            id=id, name=name, src='assets/wallpapers/' + background.name,
            thumb='assets/wallpapers/' + thumbnail.name, pos='50% 50%',
            tone=tone, credit=credit, source='https://unsplash.com/photos/' + source,
            originalBytes=path.stat().st_size, backgroundBytes=background.stat().st_size,
            thumbnailBytes=thumbnail.stat().st_size, originalSha256=original_hash,
            backgroundSha256=file_hash(background), thumbnailSha256=file_hash(thumbnail),
        ))
        print(id, 'background', background.stat().st_size, 'thumbnail', thumbnail.stat().st_size)
    # A partial run records only its selected IDs; app/SOURCES.json is never changed.
    (OUTPUT / 'SOURCES.json').write_text(json.dumps(items, indent=2) + '\n')
    print('Generated', len(items), 'backgrounds and thumbnails in', OUTPUT)
    print('Source bytes', sum(x['originalBytes'] for x in items),
          'TV background bytes', sum(x['backgroundBytes'] for x in items))
    print('Original hashes unchanged. Review staged files before copying into app assets.')


if __name__ == '__main__':
    main()
