import argparse
import datetime
import json
import os

from PIL import Image, ImageDraw

import state
from render_carousel import (
    ACCENT_BROWN,
    DARK_TEXT,
    HANDLE,
    HASHTAGS,
    TEMPLATE_CREAM,
    W,
    draw_centered_multiline,
    draw_handle,
    fit_text,
    load_bank,
    load_font,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")


def draw_cross(draw):
    cx, cy = W - 78, 62
    draw.line([(cx, cy - 16), (cx, cy + 16)], fill=ACCENT_BROWN, width=4)
    draw.line([(cx - 11, cy - 5), (cx + 11, cy - 5)], fill=ACCENT_BROWN, width=4)


def render_verse_slide(item):
    img = Image.open(TEMPLATE_CREAM).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_cross(draw)

    kicker_font = load_font("semibold", 32)
    kicker_h = draw.textbbox((0, 0), "Ag", font=kicker_font)[3] * 1.2

    quote = f"“{item['versiculo_texto']}”"
    quote_font, quote_lines, quote_line_h = fit_text(draw, quote, "bold_italic", W - 180, 700, 72, 38)
    quote_h = quote_line_h * len(quote_lines)

    ref_font = load_font("semibold", 32)
    ref_h = draw.textbbox((0, 0), "Ag", font=ref_font)[3] * 1.2

    gap1, gap2 = 40, 36
    total_h = kicker_h + gap1 + quote_h + gap2 + ref_h
    zone_top, zone_bottom = 170, 1060
    start_y = zone_top + max(0, (zone_bottom - zone_top - total_h) / 2)

    draw_centered_multiline(draw, ["VERSÍCULO DO DIA"], kicker_font, W / 2, start_y, 0, ACCENT_BROWN)
    y = start_y + kicker_h + gap1
    y = draw_centered_multiline(draw, quote_lines, quote_font, W / 2, y, quote_line_h, DARK_TEXT)
    draw_centered_multiline(draw, [item["versiculo_ref"].upper()], ref_font, W / 2, y + gap2, 0, ACCENT_BROWN)

    draw_handle(draw, dark_bg=False)
    return img


def build_caption(item):
    return (
        f"“{item['versiculo_texto']}” — {item['versiculo_ref']}\n\n"
        "\U0001F447 Comenta um AMÉM se esse versículo falou com você hoje.\n"
        "Salve para lembrar e compartilhe nos seus Stories com alguém que precisa ouvir isso agora.\n\n"
        f"{HASHTAGS}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    parser.add_argument("--slot", default="pm", choices=["am", "pm"], help="used in filename")
    parser.add_argument("--index", type=int, default=None, help="override bank index")
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    bank = load_bank()
    idx = args.index if args.index is not None else state.current_index("mensagem_index", len(bank))
    item = bank[idx]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prefix = f"versiculo_{date_str}_{args.slot}"

    slide = render_verse_slide(item)
    jpg_path = os.path.join(OUTPUT_DIR, f"{prefix}.jpg")
    slide.convert("RGB").save(jpg_path, "JPEG", quality=92)

    meta = {
        "id": item["id"],
        "tema": item["tema"],
        "caption": build_caption(item),
        "image_filename": os.path.basename(jpg_path),
    }
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK: {jpg_path}")
    print(f"OK: {meta_path}")


if __name__ == "__main__":
    main()
