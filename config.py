"""
config.py - Centralized configuration management for ASCII art generator.

This module defines default settings and a Config dataclass that controls
all aspects of ASCII art generation including character sets, scaling,
color output and export formats.
"""

from dataclasses import dataclass, field
from typing import List, Optional

# ---------------------------------------------------------------------------
# Available character sets ordered from darkest to lightest
# ---------------------------------------------------------------------------
CHAR_SETS = {
    "standard": "@%#*+=-:. ",
    "detailed": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "minimal": "@#. ",
    "blocks": "█▓▒░ ",
    "binary": "01 ",
    "symbols": "#$&@%*+=-:. ",
}

# ---------------------------------------------------------------------------
# Pyfiglet font presets
# ---------------------------------------------------------------------------
FONT_PRESETS = [
    "banner",
    "big",
    "block",
    "bubble",
    "digital",
    "ivrit",
    "lean",
    "mini",
    "script",
    "shadow",
    "slant",
    "small",
    "smscript",
    "smshadow",
    "smslant",
    "standard",
    "term",
]


@dataclass
class Config:
    """
    Central configuration object passed throughout the program.

    Attributes
    ----------
    char_set : str
        Key into CHAR_SETS or a custom string of characters.
    font : str
        Pyfiglet font name for text-to-ASCII conversion.
    scale : float
        Downsample factor for image/video frames (0 < scale ≤ 1).
    width : Optional[int]
        Force output width in characters (overrides scale when set).
    color : bool
        Whether to emit ANSI colour codes in console output.
    contrast : float
        Contrast multiplier applied to each frame before conversion.
    brightness : float
        Brightness offset (0-255) added to each frame before conversion.
    bg_color : Optional[str]
        ANSI background colour name, e.g. ``"black"``.  ``None`` = default.
    fps : float
        Playback speed (frames per second) for video-to-ASCII export.
    output_format : str
        One of ``"console"``, ``"file"``, or ``"video"``.
    output_path : Optional[str]
        Destination file path when *output_format* is ``"file"`` or ``"video"``.
    random_word_count : int
        Number of random words to generate when ``--random`` mode is used.
    """

    char_set: str = "standard"
    font: str = "standard"
    scale: float = 0.4
    width: Optional[int] = None
    color: bool = False
    contrast: float = 1.0
    brightness: float = 0.0
    bg_color: Optional[str] = None
    fps: float = 10.0
    output_format: str = "console"
    output_path: Optional[str] = None
    random_word_count: int = 1

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------
    def get_char_set(self) -> str:
        """Return the actual character string for this configuration."""
        if self.char_set in CHAR_SETS:
            return CHAR_SETS[self.char_set]
        # User supplied a custom string directly
        return self.char_set

    def validate(self) -> None:
        """Raise *ValueError* if any field has an invalid value."""
        if not (0 < self.scale <= 1):
            raise ValueError(f"scale must be in (0, 1], got {self.scale}")
        if self.contrast <= 0:
            raise ValueError(f"contrast must be positive, got {self.contrast}")
        if self.fps <= 0:
            raise ValueError(f"fps must be positive, got {self.fps}")
        if self.output_format not in ("console", "file", "video"):
            raise ValueError(
                f"output_format must be 'console', 'file', or 'video', "
                f"got '{self.output_format}'"
            )
        if self.output_format in ("file", "video") and not self.output_path:
            raise ValueError(
                "output_path must be provided when output_format is "
                f"'{self.output_format}'"
            )
