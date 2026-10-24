"""Occasional local mascots placed only in measured unoccupied card regions."""

import base64
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image

APPEARANCE_RATE = 0.4
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "easter_eggs"


def choose_position(bounds, occupied, size, rng=random):
    """Choose a fully contained position with a clear margin around protected regions.

    Args:
        bounds: Card rectangle (left, top, right, bottom).
        occupied: Protected text/image rectangles in the same coordinates.
        size: Mascot width and height.
        rng: Random generator, injectable for deterministic regression tests.

    Returns:
        Safe (x, y), or None when no suitable empty region exists.
    """
    left, top, right, bottom = bounds
    width, height = size
    candidates = [
        (x, y)
        for y in range(int(top) + 12, int(bottom - height - 12) + 1, 20)
        for x in range(int(left) + 20, int(right - width - 12) + 1, 20)
    ]
    rng.shuffle(candidates)
    for x, y in candidates[:6000]:
        if all(
            x + width + 10 <= a or x - 10 >= c or y + height + 10 <= b or y - 10 >= d
            for a, b, c, d in occupied
        ):
            return x, y
    return None


@lru_cache(maxsize=12)
def _image_data(path):
    """Cache immutable bundled image bytes for repeated local rendering.

    Args:
        path: Bundled PNG asset.

    Returns:
        A PNG data URL.
    """
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


async def decorate_html(page, rng=random):
    """Decorate a final HTML layout without covering text, media or CSS image artwork.

    Args:
        page: Loaded Playwright card page after artwork positioning.
        rng: Random generator.

    Returns:
        Placement metadata for verification, or None when skipped.
    """
    files = sorted(ASSETS.glob("*.png"))
    if not files or rng.random() >= APPEARANCE_RATE:
        return None
    layout = await page.evaluate("""() => {
        const root = document.body.firstElementChild;
        if (!root) return null;
        const rect = r => [r.left, r.top, r.right, r.bottom];
        const occupied = [];
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            const node = walker.currentNode;
            if (!node.textContent.trim()) continue;
            const parent = node.parentElement;
            if (!parent || ['STYLE','SCRIPT'].includes(parent.tagName)) continue;
            const style = getComputedStyle(parent);
            if (style.visibility === 'hidden' || style.display === 'none') continue;
            const range = document.createRange(); range.selectNodeContents(node);
            for (const r of range.getClientRects()) if (r.width && r.height) occupied.push(rect(r));
        }
        for (const el of root.querySelectorAll('*')) {
            const style = getComputedStyle(el);
            if (style.visibility === 'hidden' || style.display === 'none') continue;
            if (el.matches('img,svg,canvas,video') || style.backgroundImage.includes('url(')) {
                const r = el.getBoundingClientRect();
                if (r.width && r.height) occupied.push(rect(r));
            }
        }
        return {bounds: rect(root.getBoundingClientRect()), occupied};
    }""")
    if not layout:
        return None
    asset = rng.choice(files)
    with Image.open(asset) as original:
        ratio = original.width / original.height
    height = rng.choice([86, 96, 106])
    size = (round(height * ratio), height)
    position = choose_position(layout["bounds"], layout["occupied"], size, rng)
    if position is None:
        return None
    x, y = position
    await page.evaluate(
        """async ({src,x,y,w,h}) => {
        const image = new Image(); image.src = src;
        image.dataset.arkEasterEgg = 'true'; image.alt = '';
        Object.assign(image.style, {position:'fixed',left:x+'px',top:y+'px',width:w+'px',
            height:h+'px',objectFit:'contain',pointerEvents:'none',zIndex:'100'});
        await image.decode(); document.body.appendChild(image);
    }""",
        {"src": _image_data(asset), "x": x, "y": y, "w": size[0], "h": size[1]},
    )
    return {"asset": asset.name, "position": position, "size": size, **layout}


def decorate_picture(image, occupied, rng=random):
    """Add one optional mascot to a Pillow card using actual text bounds.

    Args:
        image: Existing RGB result card.
        occupied: Text and original image rectangles.
        rng: Random generator.

    Returns:
        Placement metadata, or None when skipped.
    """
    files = sorted(ASSETS.glob("*.png"))
    if not files or rng.random() >= APPEARANCE_RATE:
        return None
    asset = rng.choice(files)
    with Image.open(asset) as original:
        mascot = original.convert("RGBA")
    mascot.thumbnail((112, 112), Image.Resampling.LANCZOS)
    position = choose_position(
        (12, 0, image.width, image.height), occupied, mascot.size, rng
    )
    if position is None:
        return None
    image.paste(mascot, position, mascot)
    return {"asset": asset.name, "position": position, "size": mascot.size}
