"""
text_generator.py - Text-to-ASCII art generation using pyfiglet.

Provides:
- ``text_to_ascii``  – convert a string to ASCII art text.
- ``random_word``    – generate random word(s) from a built-in word list.
- ``list_fonts``     – enumerate available pyfiglet fonts.
"""

import random
from typing import List, Optional

try:
    import pyfiglet
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pyfiglet is required: pip install pyfiglet"
    ) from exc

from config import Config

# ---------------------------------------------------------------------------
# A small built-in word list so the program works without network access.
# Feel free to extend this list.
# ---------------------------------------------------------------------------
_WORD_LIST: List[str] = [
    "python", "galaxy", "ocean", "thunder", "ninja", "pixel",
    "cosmos", "dragon", "laser", "matrix", "quantum", "robot",
    "shadow", "storm", "vortex", "wizard", "zenith", "alpha",
    "blaze", "cipher", "delta", "echo", "falcon", "ghost",
    "horizon", "iris", "jungle", "karma", "lunar", "meteor",
    "nebula", "orbit", "prism", "quasar", "raptor", "solar",
    "titan", "ultra", "vapor", "wave", "xenon", "yonder",
    "zephyr", "abyss", "beam", "crystal", "dusk", "ember",
    "frost", "glow",
]


def random_word(count: int = 1) -> List[str]:
    """Return *count* randomly chosen words from the built-in word list.

    Parameters
    ----------
    count:
        How many words to return (default 1).

    Returns
    -------
    list[str]
        A list of random words.
    """
    if count <= 0:
        return []
    return random.choices(_WORD_LIST, k=count)


def list_fonts() -> List[str]:
    """Return all font names available in the installed pyfiglet package."""
    return pyfiglet.FigletFont.getFonts()


def text_to_ascii(text: str, config: Optional[Config] = None) -> str:
    """Convert *text* to an ASCII art banner using pyfiglet.

    Parameters
    ----------
    text:
        The input string to render.
    config:
        Optional :class:`Config` instance.  If omitted, default settings
        are used.

    Returns
    -------
    str
        Multi-line ASCII art string.
    """
    if config is None:
        config = Config()

    fig = pyfiglet.Figlet(font=config.font, width=config.width or 200)
    art = fig.renderText(text)

    if config.color:
        art = _colorize_text(art, config)

    return art


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
_ANSI_COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}

_ANSI_BG_COLORS = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

_RESET = "\033[0m"

# Cycling colour palette used for the banner text
_TEXT_COLOR_CYCLE = [
    _ANSI_COLORS["bright_cyan"],
    _ANSI_COLORS["bright_magenta"],
    _ANSI_COLORS["bright_yellow"],
    _ANSI_COLORS["bright_green"],
]


def _colorize_text(art: str, config: Config) -> str:
    """Wrap ASCII art lines in ANSI escape codes for coloured output."""
    bg = _ANSI_BG_COLORS.get(config.bg_color or "", "")
    result_lines = []
    for i, line in enumerate(art.splitlines()):
        fg = _TEXT_COLOR_CYCLE[i % len(_TEXT_COLOR_CYCLE)]
        result_lines.append(f"{bg}{fg}{line}{_RESET}")
    return "\n".join(result_lines)
