import os

from PIL import ImageFont

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


def _line_width(draw, words, font, space_w):
    widths = [draw.textbbox((0, 0), w, font=font)[2] for w in words]
    return widths, sum(widths) + space_w * (len(words) - 1)


def draw_paragraph_last_word_accent(draw, text, font, center_x, top_y, max_width, fill, accent_fill, line_spacing=1.15):
    """Draws a wrapped paragraph, with only the very last word colored+underlined (accent punchline)."""
    lines = wrap_text(draw, text, font, max_width)
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
    space_w = draw.textbbox((0, 0), " ", font=font)[2]
    y = top_y
    for i, line in enumerate(lines):
        words = line.split()
        widths, total_w = _line_width(draw, words, font, space_w)
        x = center_x - total_w / 2
        is_last_line = i == len(lines) - 1
        for j, (w, bw) in enumerate(zip(words, widths)):
            is_last_word = is_last_line and j == len(words) - 1
            color = accent_fill if is_last_word else fill
            draw.text((x, y), w, font=font, fill=color)
            if is_last_word:
                bbox = draw.textbbox((x, y), w, font=font)
                draw.line([(bbox[0], bbox[3] + 4), (bbox[2], bbox[3] + 4)], fill=accent_fill, width=4)
            x += bw + space_w
        y += line_h
    return y


def measure_stacked_headline(draw, before, highlight, after, bold_font, italic_font, max_width, gap=14):
    lines_before = wrap_text(draw, before.upper(), bold_font, max_width)
    lines_highlight = wrap_text(draw, highlight, italic_font, max_width)
    lines_after = wrap_text(draw, after.upper(), bold_font, max_width)
    bold_line_h = draw.textbbox((0, 0), "Ag", font=bold_font)[3] * 1.1
    italic_line_h = draw.textbbox((0, 0), "Ag", font=italic_font)[3] * 1.15
    total_h = (
        bold_line_h * len(lines_before) + gap
        + italic_line_h * len(lines_highlight) + gap
        + bold_line_h * len(lines_after)
    )
    return total_h, bold_line_h, italic_line_h


def draw_stacked_headline(draw, before, highlight, after, bold_font, italic_font, center_x, top_y, max_width, dark_fill, dim_fill, accent_fill, gap=14):
    """Draws a 3-line headline: BOLD CAPS / italic phrase / BOLD CAPS with last word underlined+accented."""
    lines_before = wrap_text(draw, before.upper(), bold_font, max_width)
    lines_highlight = wrap_text(draw, highlight, italic_font, max_width)
    lines_after = wrap_text(draw, after.upper(), bold_font, max_width)
    bold_line_h = draw.textbbox((0, 0), "Ag", font=bold_font)[3] * 1.1
    italic_line_h = draw.textbbox((0, 0), "Ag", font=italic_font)[3] * 1.15
    space_w_bold = draw.textbbox((0, 0), " ", font=bold_font)[2]

    y = top_y
    for line in lines_before:
        draw_centered_multiline(draw, [line], bold_font, center_x, y, 0, dark_fill)
        y += bold_line_h
    y += gap

    draw_centered_multiline(draw, lines_highlight, italic_font, center_x, y, italic_line_h, dim_fill)
    y += italic_line_h * len(lines_highlight) + gap

    for i, line in enumerate(lines_after):
        words = line.split()
        widths, total_w = _line_width(draw, words, bold_font, space_w_bold)
        x = center_x - total_w / 2
        is_last_line = i == len(lines_after) - 1
        for j, (w, bw) in enumerate(zip(words, widths)):
            is_last_word = is_last_line and j == len(words) - 1
            color = accent_fill if is_last_word else dark_fill
            draw.text((x, y), w, font=bold_font, fill=color)
            if is_last_word:
                bbox = draw.textbbox((x, y), w, font=bold_font)
                draw.line([(bbox[0], bbox[3] + 4), (bbox[2], bbox[3] + 4)], fill=accent_fill, width=4)
            x += bw + space_w_bold
        y += bold_line_h
    return y
