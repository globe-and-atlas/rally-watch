"""Build a GIF-first gallery from verified native palette captures."""
from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    store = ROOT / 'media/store'
    spec = json.loads((store / 'spec.json').read_text())
    frames = [Image.open(ROOT / 'media' / name).convert('RGB') for name in spec['frames']]
    assert all(frame.size == (200, 228) for frame in frames)
    durations = [3000] + [2500] * (len(frames) - 1)
    gif = store / 'emery_01_palettes.gif'
    frames[0].save(gif, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=2, optimize=False)
    with Image.open(gif) as decoded:
        assert decoded.n_frames == len(frames)
        assert decoded.info['loop'] == 0
        for index, original in enumerate(frames):
            decoded.seek(index)
            assert decoded.convert('RGB').tobytes() == original.tobytes()
            assert decoded.info['duration'] == durations[index]
    screenshots = [gif.name]
    for index, source in enumerate(spec['stills'], start=2):
        path = store / f'emery_{index:02}_palette.png'
        shutil.copy2(ROOT / 'media' / spec['frames'][source], path)
        screenshots.append(path.name)
    for size, name in [(80, 'small'), (144, 'large')]:
        source = frames[0].crop(spec['icon_crop']) if size == 80 else frames[0]
        icon = Image.new('RGB', (size, size), frames[0].getpixel((0, 0)))
        fitted = ImageOps.contain(source, (size - 8, size - 8), Image.Resampling.NEAREST)
        icon.paste(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
        icon.save(store / f'icon-{name}.png')
    manifest = {'name': spec['name'], 'screenshots': screenshots,
                'frame_sources': spec['frames'], 'palette_names': spec['labels'],
                'durations_ms': durations, 'size': [200, 228],
                'gif_sha256': hashlib.sha256(gif.read_bytes()).hexdigest()}
    (store / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"PASS: {spec['name']} GIF: {len(frames)} exact native frames, {sum(durations)/1000:g}s loop; four stills; 80/144px icons")


if __name__ == '__main__':
    main()
