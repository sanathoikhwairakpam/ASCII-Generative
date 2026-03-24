"""
main.py - CLI entry point for the ASCII art generator.

Usage examples
--------------
# Text-to-ASCII (specific word)
python main.py text --word "Hello"

# Text-to-ASCII (random word)
python main.py text --random

# Text-to-ASCII with font and colour
python main.py text --word "Python" --font slant --color

# List available fonts
python main.py text --list-fonts

# Convert an image to ASCII
python main.py image path/to/image.jpg

# Convert a video to ASCII (console playback)
python main.py video path/to/clip.mp4

# Convert a video to ASCII and save as text file
python main.py video path/to/clip.mp4 --output-format file --output ascii_video.txt

# Convert a video to ASCII and re-render as video
python main.py video path/to/clip.mp4 --output-format video --output ascii_video.mp4
"""

import argparse
import sys

from config import Config, CHAR_SETS, FONT_PRESETS
from text_generator import text_to_ascii, random_word, list_fonts
from image_processor import file_to_ascii


def _build_common_args(parser: argparse.ArgumentParser) -> None:
    """Add customisation arguments that are shared across sub-commands."""
    parser.add_argument(
        "--char-set",
        default="standard",
        choices=list(CHAR_SETS.keys()) + ["custom"],
        help="Character set to use for image/video conversion (default: standard).",
    )
    parser.add_argument(
        "--custom-chars",
        default=None,
        metavar="CHARS",
        help="Custom character string when --char-set custom is used.",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=0.4,
        help="Downsample scale factor for image/video (0 < scale ≤ 1, default: 0.4).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Force output width in characters (overrides --scale).",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        default=False,
        help="Enable ANSI colour output.",
    )
    parser.add_argument(
        "--contrast",
        type=float,
        default=1.0,
        help="Contrast multiplier (default: 1.0).",
    )
    parser.add_argument(
        "--brightness",
        type=float,
        default=0.0,
        help="Brightness offset -255 to 255 (default: 0).",
    )
    parser.add_argument(
        "--bg-color",
        default=None,
        metavar="COLOR",
        help="ANSI background colour name (e.g. black, blue).",
    )
    parser.add_argument(
        "--output-format",
        default="console",
        choices=["console", "file", "video"],
        help="Where to send the output (default: console).",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Output file path (required when --output-format is file or video).",
    )


def _make_config(args: argparse.Namespace, font: str = "standard") -> Config:
    """Build a :class:`Config` from parsed CLI arguments."""
    char_set = args.char_set
    if char_set == "custom":
        if not args.custom_chars:
            print(
                "Error: --custom-chars must be provided when --char-set custom is used.",
                file=sys.stderr,
            )
            sys.exit(1)
        char_set = args.custom_chars

    return Config(
        char_set=char_set,
        font=font,
        scale=args.scale,
        width=args.width,
        color=args.color,
        contrast=args.contrast,
        brightness=args.brightness,
        bg_color=args.bg_color,
        output_format=args.output_format,
        output_path=args.output,
    )


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------

def cmd_text(args: argparse.Namespace) -> None:
    """Handle the ``text`` sub-command."""
    if args.list_fonts:
        fonts = list_fonts()
        print("\n".join(sorted(fonts)))
        return

    font = getattr(args, "font", "standard") or "standard"
    config = _make_config(args, font=font)

    if args.random:
        words = random_word(args.random_count)
    elif args.word:
        words = [args.word]
    else:
        print("Error: provide --word TEXT or --random.", file=sys.stderr)
        sys.exit(1)

    for word in words:
        art = text_to_ascii(word, config)
        _output(art, config)


def cmd_image(args: argparse.Namespace) -> None:
    """Handle the ``image`` sub-command."""
    config = _make_config(args)
    try:
        art = file_to_ascii(args.image_path, config)
    except FileNotFoundError:
        print(f"Error: image file not found: {args.image_path}", file=sys.stderr)
        sys.exit(1)
    _output(art, config)


def cmd_video(args: argparse.Namespace) -> None:
    """Handle the ``video`` sub-command."""
    # Import here to avoid requiring cv2 when only text/image modes are used
    from video_processor import (
        play_video_in_console,
        save_video_as_text,
        save_video_as_video,
    )

    config = _make_config(args)
    config.fps = args.fps

    fmt = args.output_format
    try:
        if fmt == "console":
            play_video_in_console(args.video_path, config)
        elif fmt == "file":
            if not args.output:
                print(
                    "Error: --output PATH is required with --output-format file.",
                    file=sys.stderr,
                )
                sys.exit(1)
            save_video_as_text(args.video_path, args.output, config)
            print(f"Saved ASCII video text to: {args.output}")
        elif fmt == "video":
            if not args.output:
                print(
                    "Error: --output PATH is required with --output-format video.",
                    file=sys.stderr,
                )
                sys.exit(1)
            save_video_as_video(args.video_path, args.output, config)
            print(f"Saved ASCII video to: {args.output}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Output helper
# ---------------------------------------------------------------------------

def _output(content: str, config: Config) -> None:
    """Print, save to file, or show content depending on *config*."""
    if config.output_format == "console":
        print(content)
    elif config.output_format == "file":
        if not config.output_path:
            print(
                "Error: --output PATH is required with --output-format file.",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(config.output_path, "w", encoding="utf-8") as fh:
            fh.write(content + "\n")
        print(f"Saved to: {config.output_path}")
    else:
        # "video" doesn't make sense for text/image — fall back to console
        print(content)


# ---------------------------------------------------------------------------
# Argument parser construction
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="ascii-gen",
        description="ASCII Art Generator – text, images, and videos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- text sub-command ------------------------------------------------
    text_p = sub.add_parser("text", help="Generate ASCII art from text.")
    text_p.add_argument("--word", "-w", default=None, help="Word or phrase to render.")
    text_p.add_argument(
        "--random",
        "-r",
        action="store_true",
        default=False,
        help="Generate from a random word.",
    )
    text_p.add_argument(
        "--random-count",
        type=int,
        default=1,
        metavar="N",
        help="Number of random words when --random is used (default: 1).",
    )
    text_p.add_argument(
        "--font",
        "-f",
        default="standard",
        help=f"Pyfiglet font name (default: standard). "
             f"Popular choices: {', '.join(FONT_PRESETS[:6])}. "
             f"Use --list-fonts to see all.",
    )
    text_p.add_argument(
        "--list-fonts",
        action="store_true",
        default=False,
        help="Print all available pyfiglet font names and exit.",
    )
    _build_common_args(text_p)
    text_p.set_defaults(func=cmd_text)

    # ---- image sub-command -----------------------------------------------
    image_p = sub.add_parser("image", help="Convert an image file to ASCII art.")
    image_p.add_argument("image_path", help="Path to the image file.")
    _build_common_args(image_p)
    image_p.set_defaults(func=cmd_image)

    # ---- video sub-command -----------------------------------------------
    video_p = sub.add_parser("video", help="Convert a video file to ASCII art.")
    video_p.add_argument("video_path", help="Path to the video file.")
    video_p.add_argument(
        "--fps",
        type=float,
        default=10.0,
        help="Playback / export frame rate (default: 10).",
    )
    _build_common_args(video_p)
    video_p.set_defaults(func=cmd_video)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and dispatch to the appropriate sub-command."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
