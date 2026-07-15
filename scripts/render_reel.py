import argparse
import datetime
import json
import os
import subprocess

import state
from render_carousel import HASHTAGS, load_bank, render_slide1, render_slide2, render_slide3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")

FPS = 25
SLIDE_DURATION = 4.5
XFADE_DUR = 0.6


def make_segment(image_path, out_path):
    frames = int(SLIDE_DURATION * FPS)
    vf = (
        f"scale=1080:1350,zoompan=z='min(zoom+0.0004,1.045)':d={frames}:s=1080x1350:fps={FPS},"
        "format=yuv420p"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", image_path, "-vf", vf, "-t", str(SLIDE_DURATION),
         "-pix_fmt", "yuv420p", out_path],
        check=True, capture_output=True,
    )


def concat_with_xfade(segment_paths, out_path):
    n = len(segment_paths)
    inputs = []
    for s in segment_paths:
        inputs += ["-i", s]

    filter_parts = []
    prev = "0"
    cumulative = SLIDE_DURATION
    for i in range(1, n):
        offset = cumulative - XFADE_DUR
        label = f"v{i}"
        filter_parts.append(f"[{prev}][{i}]xfade=transition=fade:duration={XFADE_DUR}:offset={offset}[{label}]")
        prev = label
        cumulative += SLIDE_DURATION - XFADE_DUR
    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex", filter_complex,
        "-map", f"[{prev}]",
        "-map", f"{n}:a",
        "-shortest",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-movflags", "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def build_reel_caption(item):
    return (
        f"{item['abertura']}\n\n"
        f"“{item['versiculo_texto']}” — {item['versiculo_ref']}\n\n"
        "\U0001F447 Comenta um AMÉM se esse versículo falou com você hoje.\n"
        "Salve e compartilhe nos seus Stories com quem precisa ouvir isso agora.\n\n"
        f"{HASHTAGS}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    parser.add_argument("--index", type=int, default=None, help="override bank index")
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    bank = load_bank()
    idx = args.index if args.index is not None else state.current_index("mensagem_index", len(bank))
    item = bank[idx]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prefix = f"reel_{date_str}"

    slides = [render_slide1(item), render_slide2(item), render_slide3(item)]
    frame_paths = []
    for i, slide in enumerate(slides, start=1):
        p = os.path.join(OUTPUT_DIR, f"{prefix}_frame{i}.jpg")
        slide.convert("RGB").save(p, "JPEG", quality=92)
        frame_paths.append(p)

    seg_paths = []
    for i, p in enumerate(frame_paths, start=1):
        seg_path = os.path.join(OUTPUT_DIR, f"{prefix}_seg{i}.mp4")
        make_segment(p, seg_path)
        seg_paths.append(seg_path)

    video_path = os.path.join(OUTPUT_DIR, f"{prefix}.mp4")
    concat_with_xfade(seg_paths, video_path)

    for p in frame_paths + seg_paths:
        os.remove(p)

    meta = {
        "id": item["id"],
        "tema": item["tema"],
        "caption": build_reel_caption(item),
        "video_filename": os.path.basename(video_path),
    }
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK: {video_path}")
    print(f"OK: {meta_path}")


if __name__ == "__main__":
    main()
