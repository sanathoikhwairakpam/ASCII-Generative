"""
image_processor.py - Convert images (and individual video frames) to ASCII art.

The core algorithm:
1. Resize the image according to *scale* / *width* settings.
2. Convert to grayscale.
3. Apply contrast and brightness adjustments.
4. Map each pixel's luminance to a character from the configured char set.
5. Optionally wrap each character in ANSI colour codes (using the original
   RGB value of that pixel).
"""

from typing import Optional

try:
    from PIL import Image, ImageEnhance
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Pillow and numpy are required: pip install Pillow numpy"
    ) from exc

from config import Config

_RESET = "\033[0m"


def _ansi_fg(r: int, g: int, b: int) -> str:
    """Return the ANSI 24-bit foreground escape for the given RGB values."""
    return f"\033[38;2;{r};{g};{b}m"


def image_to_ascii(image: "Image.Image", config: Optional[Config] = None) -> str:
    """Convert a PIL *Image* to an ASCII art string.

    Parameters
    ----------
    image:
        Source PIL Image (any mode; will be converted internally).
    config:
        Optional :class:`Config` controlling char set, scale, colour, etc.

    Returns
    -------
    str
        Multi-line string where each character represents one pixel block.
    """
    if config is None:
        config = Config()

    chars = config.get_char_set()

    # ------------------------------------------------------------------
    # Resize to target dimensions
    # ------------------------------------------------------------------
    orig_w, orig_h = image.size
    if config.width:
        # Preserve aspect ratio; characters are roughly twice as tall as wide
        target_w = config.width
        target_h = int(orig_h * target_w / orig_w * 0.45)
    else:
        target_w = max(1, int(orig_w * config.scale))
        target_h = max(1, int(orig_h * config.scale * 0.45))

    # Keep a colour copy for coloured output before grayscale conversion
    rgb_image: Optional["Image.Image"] = None
    if config.color:
        rgb_image = image.convert("RGB").resize(
            (target_w, target_h), Image.LANCZOS
        )

    gray = image.convert("L").resize((target_w, target_h), Image.LANCZOS)

    # ------------------------------------------------------------------
    # Contrast & brightness adjustment
    # ------------------------------------------------------------------
    if config.contrast != 1.0:
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(config.contrast)

    if config.brightness != 0.0:
        gray_arr = np.array(gray, dtype=np.int32)
        gray_arr = np.clip(gray_arr + int(config.brightness), 0, 255).astype(np.uint8)
        gray = Image.fromarray(gray_arr, mode="L")

    # ------------------------------------------------------------------
    # Map pixels → characters
    # ------------------------------------------------------------------
    gray_arr = np.array(gray)
    num_chars = len(chars)

    rows = []
    for y in range(target_h):
        row_chars = []
        for x in range(target_w):
            luminance = int(gray_arr[y, x])
            char_idx = int(luminance / 255 * (num_chars - 1))
            char = chars[char_idx]

            if config.color and rgb_image is not None:
                r, g, b = rgb_image.getpixel((x, y))
                char = f"{_ansi_fg(r, g, b)}{char}{_RESET}"

            row_chars.append(char)
        rows.append("".join(row_chars))

    return "\n".join(rows)


def file_to_ascii(image_path: str, config: Optional[Config] = None) -> str:
    """Load an image file and convert it to ASCII art.

    Parameters
    ----------
    image_path:
        Path to any image format supported by Pillow.
    config:
        Optional :class:`Config`.

    Returns
    -------
    str
        ASCII art string.
    """
    img = Image.open(image_path)
    return image_to_ascii(img, config)
