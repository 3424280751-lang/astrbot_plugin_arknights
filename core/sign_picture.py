"""Offline sign-in summary cards without external image dependencies."""

import hashlib
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .easter_eggs import decorate_picture


def render_sign_picture(title: str, lines: list[str], folder: Path) -> Path:
    """Render all result rows, wrapping long names and awards without truncation.

    Args:
        title: Summary title including the actual result date.
        lines: Real outcome lines, never fabricated awards.
        folder: Plugin data folder.

    Returns:
        Local PNG path for the summary.
    """
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/simhei.ttf")
    font = ImageFont.truetype(str(font_path), 28)
    heading = ImageFont.truetype(str(font_path), 38)
    small = ImageFont.truetype(str(font_path), 21)
    rows = [
        textwrap.wrap(str(line), width=29, replace_whitespace=False) or [""]
        for line in lines
    ]
    height = 180 + sum(44 * len(row) + 30 for row in rows)
    image = Image.new("RGB", (1040, max(260, height)), "#101b28")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 12, image.height), fill="#49c6bd")
    draw.text((48, 28), "RHODES ISLAND  /  罗德岛终端", font=small, fill="#72cfc7")
    draw.text((48, 68), title, font=heading, fill="#f1f5fa")
    occupied = [
        draw.textbbox((48, 28), "RHODES ISLAND  /  罗德岛终端", font=small),
        draw.textbbox((48, 68), title, font=heading),
    ]
    y = 142
    for source, row in zip(lines, rows, strict=True):
        color = "#73ddad" if "签到成功" in source or "已签到" in source else "#f3c17c"
        draw.rounded_rectangle(
            (36, y - 8, 1004, y + len(row) * 44 + 8), radius=12, fill="#1d2d40"
        )
        for line in row:
            occupied.append(draw.textbbox((56, y), line, font=font))
            draw.text((56, y), line, font=font, fill=color)
            y += 44
        y += 30
    try:
        decorate_picture(image, occupied)
    except Exception:
        pass  # Decoration must not interrupt sign-in notification delivery.
    digest = hashlib.sha256((title + "\n" + "\n".join(lines)).encode()).hexdigest()[:20]
    output = folder / "sign_cards" / (digest + ".png")
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".tmp")
    image.save(temp, format="PNG")
    temp.replace(output)
    return output
