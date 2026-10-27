"""Encode the 4K video-layer wallpaper clips from prepared 3840 x 2160 crops.

Run scripts/prepare-wallpapers.py first; it writes .local/materials/wallpapers/<id>-4k.jpg.
Each clip is two seconds of the still: H.264 High, Level 5.1, 30 fps, limited-range BT.709.
The TV pauses on a frame at one second, so only the first keyframe really matters.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CROPS = ROOT / '.local/materials/wallpapers'
OUTPUT = ROOT / 'app/assets/uhd'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Comma-separated wallpaper IDs; default: every catalogue entry')
    args = parser.parse_args()
    if not shutil.which('ffmpeg'):
        parser.error('ffmpeg is required.')
    known = [wall['id'] for wall in json.loads((ROOT / 'app/assets/wallpapers/SOURCES.json').read_text())]
    ids = known if args.ids is None else [id.strip() for id in args.ids.split(',')]
    if set(ids) - set(known):
        parser.error('Unknown wallpaper IDs: ' + ', '.join(sorted(set(ids) - set(known))))
    missing = [str(CROPS / (id + '-4k.jpg')) for id in ids if not (CROPS / (id + '-4k.jpg')).is_file()]
    if missing:
        parser.error('Missing 4K crops (run prepare-wallpapers.py):\n' + '\n'.join(missing))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for id in ids:
        clip = OUTPUT / (id + '.mp4')
        subprocess.run([
            'ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', '30', '-i', str(CROPS / (id + '-4k.jpg')),
            '-t', '2', '-vf', 'scale=3840:2160:out_color_matrix=bt709:out_range=tv,format=yuv420p',
            '-c:v', 'libx264', '-profile:v', 'high', '-level:v', '5.1', '-preset', 'slow', '-crf', '14',
            '-tune', 'stillimage', '-g', '60',
            '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709:range=tv',
            '-movflags', '+faststart', '-an', str(clip),
        ], check=True)
        print(id, clip.stat().st_size)
    print('Encoded', len(ids), 'clips in', OUTPUT)


if __name__ == '__main__':
    main()
