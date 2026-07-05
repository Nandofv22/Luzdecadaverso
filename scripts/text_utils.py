import os

from PIL import ImageFont


def measure_headline(draw, plain_before, highlight_word, plain_after, font, max_width, line_spacing=1.15):
    full_text = f"{plain_before} {highlight_word} {plain_after}".strip()
    lines = wrap_text(draw, full_text, font, max_width)
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
    return lines, line_h, line_h * len(lines)

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(HERE, "..", "assets", "fonts")

FONTS = {
    "bold": os.path.join(FONTS_DIR, "Poppins-Bold.ttf"),
    "semibold": os.path.join(FONTS_DIR, "Poppins-SemiBold.ttf"),
    "medium": os.path.join(FONTS_DIR, "Poppins-Medium.ttf"),
    "italic": os.path.join(FONTS_DIR, "PlayfairDisplay-Italic.ttf"),
    "bold_italic": os.path.join(FONTS_DIR, "PlayfairDisplay-BoldItalic.ttf"),
}

_VARIABLE_WEIGHTS = {
    "italic": 500,
    "bold_italic": 800,
}


def load_font(kind, size):
    font = ImageFont.truetype(FONTS[kind], size)
    if kind in _VARIABLE_WEIGHTS:
        try:
            font.set_variation_by_axes([_VARIABLE_WEIGHTS[kind]])
        except Exception:
            pass
    return font


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        w = draw.textbbox((0, 0), candidate, font=font)[2]
        if w <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_text(draw, text, kind, max_width, max_height, max_size, min_size, line_spacing=1.25, step=2):
    best_font, best_lines = None, None
    for size in range(max_size, min_size - 1, -step):
        font = load_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
        total_h = line_h * len(lines)
        best_font, best_lines = font, lines
        if total_h <= max_height:
            return font, lines, line_h
    font = load_font(kind, min_size)
    lines = wrap_text(draw, text, font, max_width)
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
    return font, lines, line_h


def draw_centered_multiline(draw, lines, font, center_x, top_y, line_h, fill, align="center", box_left=None, box_right=None):
    y = top_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        if align == "center":
            x = center_x - w / 2
        elif align == "left":
            x = box_left
        else:
            x = box_right - w
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_mixed_headline(draw, plain_before, highlight_word, plain_after, font, center_x, top_y, max_width, fill, highlight_fill):
    """Draws a headline that may wrap, with one word highlighted in a different color, centered."""
    full_text = f"{plain_before} {highlight_word} {plain_after}".strip()
    lines = wrap_text(draw, full_text, font, max_width)
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * 1.15
    y = top_y
    for line in lines:
        words = line.split()
        widths = []
        total_w = 0
        space_w = draw.textbbox((0, 0), " ", font=font)[2]
        for w in words:
            bw = draw.textbbox((0, 0), w, font=font)[2]
            widths.append(bw)
            total_w += bw
        total_w += space_w * (len(words) - 1)
        x = center_x - total_w / 2
        for w, bw in zip(words, widths):
            color = highlight_fill if w.strip(".,!?”“") == highlight_word.strip(".,!?") else fill
            draw.text((x, y), w, font=font, fill=color)
            x += bw + space_w
        y += line_h
    return y
