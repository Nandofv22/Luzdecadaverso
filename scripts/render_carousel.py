import argparse
import datetime
import json
import os

from PIL import Image, ImageDraw

import state
from text_utils import (
    draw_centered_multiline,
    draw_chunk_lines,
    draw_paragraph_last_word_accent,
    fit_text,
    load_font,
    measure_chunk_lines,
    wrap_text,
)

CONTENT_ZONE_TOP = 180
CONTENT_ZONE_BOTTOM = 950

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA_PATH = os.path.join(ROOT, "data", "mensagens.json")
TEMPLATE_CREAM = os.path.join(ROOT, "assets", "template_cream.png")
TEMPLATE_DARK = os.path.join(ROOT, "assets", "template_dark.png")
OUTPUT_DIR = os.path.join(ROOT, "output")

W, H = 1080, 1350

DARK_TEXT = (58, 40, 24)
DIM_TEXT = (110, 88, 64)
ACCENT_BROWN = (150, 84, 30)
CREAM_TEXT = (250, 242, 228)
CREAM_DIM = (222, 195, 160)
ACCENT_GOLD = (216, 155, 84)

HANDLE = "@luzdecadaverso"

HASHTAGS = (
    "#luzdecadaverso #versiculododia #palavradedeus #fe #devocional "
    "#reflexaododia #deuseFiel #biblia #motivacaocrista"
)


def load_bank():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["mensagens"]


def draw_progress_bar(draw, active_index, total=3):
    margin = 100
    gap = 14
    total_w = W - 2 * margin
    seg_w = (total_w - gap * (total - 1)) / total
    y0, y1 = H - 78, H - 74
    for i in range(total):
        x0 = margin + i * (seg_w + gap)
        x1 = x0 + seg_w
        color = ACCENT_BROWN if i <= active_index else (200, 180, 150)
        draw.rounded_rectangle([x0, y0, x1, y1], radius=2, fill=color)


def draw_counter_and_cross(draw, index, total, dark_bg):
    color = CREAM_DIM if dark_bg else DIM_TEXT
    counter_font = load_font("semibold", 20)
    draw.text((60, 50), f"0{index + 1} / 0{total}", font=counter_font, fill=color)
    # simple cross ornament, top right
    cx, cy = W - 78, 62
    cross_color = CREAM_DIM if dark_bg else ACCENT_BROWN
    draw.line([(cx, cy - 16), (cx, cy + 16)], fill=cross_color, width=4)
    draw.line([(cx - 11, cy - 5), (cx + 11, cy - 5)], fill=cross_color, width=4)


def draw_handle(draw, dark_bg):
    color = CREAM_DIM if dark_bg else DIM_TEXT
    font = load_font("medium", 24)
    draw_centered_multiline(draw, [HANDLE], font, W / 2, H - 130, 0, color)


def render_slide1(item):
    img = Image.open(TEMPLATE_CREAM).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_counter_and_cross(draw, 0, 3, dark_bg=False)

    kicker_font = load_font("semibold", 28)
    kicker_h = draw.textbbox((0, 0), "Ag", font=kicker_font)[3] * 1.2

    headline_font = load_font("bold", 66)
    italic_font = load_font("italic", 46)
    headline_h, resolved_chunks = measure_chunk_lines(
        draw, item["headline_chunks"], headline_font, italic_font, W - 160,
    )

    sub_font, sub_lines, sub_line_h = fit_text(draw, item["subtitle1"], "italic", W - 260, 260, 38, 26)
    sub_h = sub_line_h * len(sub_lines)

    gap1, gap2 = 30, 44
    total_h = kicker_h + gap1 + headline_h + gap2 + sub_h
    start_y = CONTENT_ZONE_TOP + max(0, (CONTENT_ZONE_BOTTOM - CONTENT_ZONE_TOP - total_h) / 2)

    draw_centered_multiline(draw, [item["kicker1"]], kicker_font, W / 2, start_y, 0, ACCENT_BROWN)
    y = start_y + kicker_h + gap1
    y = draw_chunk_lines(draw, resolved_chunks, W / 2, y, DARK_TEXT, DIM_TEXT, ACCENT_BROWN)
    draw_centered_multiline(draw, sub_lines, sub_font, W / 2, y + gap2, sub_line_h, DIM_TEXT)

    draw_handle(draw, dark_bg=False)
    draw_progress_bar(draw, 0)
    return img


def render_slide2(item):
    img = Image.open(TEMPLATE_DARK).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_counter_and_cross(draw, 1, 3, dark_bg=True)

    kicker_font = load_font("semibold", 28)
    kicker_h = draw.textbbox((0, 0), "Ag", font=kicker_font)[3] * 1.2

    quote = f"“{item['versiculo_texto']}”"
    quote_font, quote_lines, quote_line_h = fit_text(draw, quote, "bold_italic", W - 200, 600, 60, 34)
    quote_h = quote_line_h * len(quote_lines)

    ref_font = load_font("semibold", 28)
    ref_h = draw.textbbox((0, 0), "Ag", font=ref_font)[3] * 1.2

    gap1, gap2 = 44, 34
    total_h = kicker_h + gap1 + quote_h + gap2 + ref_h
    start_y = CONTENT_ZONE_TOP + max(0, (CONTENT_ZONE_BOTTOM - CONTENT_ZONE_TOP - total_h) / 2)

    draw_centered_multiline(draw, [item["kicker2"]], kicker_font, W / 2, start_y, 0, ACCENT_GOLD)
    y = start_y + kicker_h + gap1
    y = draw_centered_multiline(draw, quote_lines, quote_font, W / 2, y, quote_line_h, CREAM_TEXT)
    draw_centered_multiline(draw, [item["versiculo_ref"].upper()], ref_font, W / 2, y + gap2, 0, ACCENT_GOLD)

    draw_handle(draw, dark_bg=True)
    draw_progress_bar(draw, 1)
    return img


def render_slide3(item):
    img = Image.open(TEMPLATE_CREAM).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw_counter_and_cross(draw, 2, 3, dark_bg=False)

    kicker_font = load_font("semibold", 28)
    kicker_h = draw.textbbox((0, 0), "Ag", font=kicker_font)[3] * 1.2

    headline_font = load_font("bold", 64)
    cta_text = f"{item['cta_before']} {item['cta_highlight']} {item['cta_after']}".strip()
    cta_lines = wrap_text(draw, cta_text, headline_font, W - 160)
    headline_line_h = draw.textbbox((0, 0), "Ag", font=headline_font)[3] * 1.15
    headline_h = headline_line_h * len(cta_lines)

    sub_font, sub_lines, sub_line_h = fit_text(draw, item["cta_subtitle"], "italic", W - 260, 200, 34, 24)
    sub_h = sub_line_h * len(sub_lines)

    btn_font = load_font("semibold", 32)
    btn_text = "Salve para lembrar"
    bbox = draw.textbbox((0, 0), btn_text, font=btn_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 46, 24
    btn_h = th + pad_y * 2

    share_font = load_font("italic", 28)
    share_h = draw.textbbox((0, 0), "Ag", font=share_font)[3] * 1.2

    gap1, gap2, gap3, gap4 = 28, 40, 46, 30
    total_h = kicker_h + gap1 + headline_h + gap2 + sub_h + gap3 + btn_h + gap4 + share_h
    start_y = CONTENT_ZONE_TOP + max(0, (CONTENT_ZONE_BOTTOM - CONTENT_ZONE_TOP - total_h) / 2)

    draw_centered_multiline(draw, [item["kicker3"]], kicker_font, W / 2, start_y, 0, ACCENT_BROWN)
    y = start_y + kicker_h + gap1
    y = draw_paragraph_last_word_accent(
        draw, cta_text, headline_font, W / 2, y, W - 160, DARK_TEXT, ACCENT_BROWN,
    )
    y = draw_centered_multiline(draw, sub_lines, sub_font, W / 2, y + gap2, sub_line_h, DIM_TEXT)

    btn_top = y + gap3
    box = [W / 2 - tw / 2 - pad_x, btn_top, W / 2 + tw / 2 + pad_x, btn_top + th + pad_y * 2]
    draw.rounded_rectangle(box, radius=34, fill=ACCENT_BROWN)
    draw.text((W / 2 - tw / 2, btn_top + pad_y - bbox[1]), btn_text, font=btn_font, fill=(250, 242, 228))

    draw_centered_multiline(draw, ["Compartilhe essa luz"], share_font, W / 2, box[3] + gap4, 0, DIM_TEXT)

    draw_handle(draw, dark_bg=False)
    draw_progress_bar(draw, 2)
    return img


def build_caption(item):
    return (
        f"{item['abertura']}\n\n"
        f"{item['subtitle1']}\n\n"
        f"“{item['versiculo_texto']}” — {item['versiculo_ref']}\n\n"
        "\U0001F447 Comenta um AMÉM se esse versículo falou com você hoje.\n"
        "Salve para lembrar nos dias mais corridos e compartilhe nos seus Stories "
        "pra alguém que também precisa ouvir isso agora.\n\n"
        f"{HASHTAGS}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    parser.add_argument("--slot", default="am", choices=["am", "pm"], help="am=9h, pm=19h (used in filename)")
    parser.add_argument("--index", type=int, default=None, help="override bank index")
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    bank = load_bank()
    idx = args.index if args.index is not None else state.current_index("mensagem_index", len(bank))
    item = bank[idx]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    prefix = f"carrossel_{date_str}_{args.slot}"

    slide1 = render_slide1(item)
    slide2 = render_slide2(item)
    slide3 = render_slide3(item)

    paths = []
    for i, slide in enumerate([slide1, slide2, slide3], start=1):
        jpg_path = os.path.join(OUTPUT_DIR, f"{prefix}_slide{i}.jpg")
        slide.convert("RGB").save(jpg_path, "JPEG", quality=92)
        paths.append(jpg_path)

    meta = {
        "id": item["id"],
        "tema": item["tema"],
        "caption": build_caption(item),
        "image_filenames": [os.path.basename(p) for p in paths],
    }
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    for p in paths:
        print(f"OK: {p}")
    print(f"OK: {meta_path}")


if __name__ == "__main__":
    main()
