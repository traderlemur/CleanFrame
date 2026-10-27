# Asset generation

The app includes all runtime JPEGs, thumbnails, registered material fields, public fonts and icons. A clone can preview the current app without the original Downloads folder or any generation step. Keep photo and icon credits and third-party licences with the assets. The private Pangram overlay is described in [development](development.md).

## Current List and Dock materials

The runtime uses twenty-four photographs. Each has a background, a thumbnail, a small panel backdrop and four full-stage material JPEGs. The runtime never generates blur or reads photo pixels. Generate selected materials with:

```sh
node scripts/build-materials.mjs summit,goldcoast,sydney,amber,mint,alpine
```

Omit the argument to regenerate every catalogue entry. Output goes to ignored `.local/materials/builder/`. Review it, then copy `*-panel.jpg` to `app/assets/wallpapers/` and the other four JPEGs to `app/assets/materials/`.

- `field-blur`: 28px blur, saturation .92, mirrored edge padding and highlight soft clipping.
- `field-frost`: the same registered crop with 42px blur.
- `field-clear`: 2px blur and saturation 1.06, with no baked veil.
- `study-soft`: the retained name for the reviewed Dock Soft recipe, including the lower scrim, 14px blur and compressed local variation. The original nine preserve their calibrated tint. New photos use a bounded tint selected from the dock band.

All fields use the centred 1920 x 1080 crop. The small panel backdrop comes from that same Frost field. The six new backgrounds use baseline sRGB JPEG at quality 90 with full chroma; thumbnails use quality 85. Their originals remain unchanged.

`app/assets/wallpapers/catalog.js` stores names and surface parameters; `app/assets/adaptive-ink.js` stores offline colour choices. New photographs need a rendered review of their List, Dock, clock, controls and all three materials before their metadata is accepted. An average image colour alone does not establish readable text.

## Icon metrics

`node scripts/build-icon-metrics.mjs` measures the SVGs in an aspect-preserved 240px viewport, matching the CSS mask renderer. Output is ignored `.local/materials/metrics.js`; review before copying it into `app/assets/icons/metrics.js`. The TV reads these bounds and does not scan icon pixels.

## New or replacement photographs

The current set is twenty-four Unsplash photographs (twenty-two of Shanghai, one of New York and one of Tokyo), downloaded as 3840px renditions into ignored `.local/originals/shanghai/` (`picks.tsv` lists id, name, photo ID, CDN image and credit). Prepare them with Pillow in a local environment:

```sh
python3 -m venv .local/venv && .local/venv/bin/pip install Pillow
.local/venv/bin/python scripts/prepare-wallpapers.py .local/originals/shanghai
```

This writes centred 1920 x 1080 backgrounds (quality 90, full chroma), 512 x 288 thumbnails and 3840 x 2160 `-4k.jpg` crops to `.local/materials/wallpapers/`. The 4K crops feed the video-layer wallpaper. `python3 scripts/encode-uhd.py` (ffmpeg required; `--ids` for a subset) encodes each as a two-second H.264 High, Level 5.1, limited-range BT.709 MP4 in `app/assets/uhd/`, about 3–5 MB each. Samsung TV apps draw their UI at 1920 x 1080; only the video plane is UHD, so the clip is the only way to show the photo at full resolution. Keep the clip's crop identical to the background, which every material is registered to.

For another photo, add its source/credit to `SOURCES.json`, prepare its background, thumbnail and 4K clip, add the gallery entry in `catalog.js`, generate the four registered materials and panel backdrop, then review its clock, controls and dock in both layouts. Keep the crop identical across all assets. Run source and browser checks before packaging.
