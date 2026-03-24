"""
video_processor.py - Video-to-ASCII conversion using OpenCV.

Workflow
--------
1. Open a video file with ``cv2.VideoCapture``.
2. Extract frames one by one, converting each to a PIL Image.
3. Pass each PIL Image through :func:`image_processor.image_to_ascii`.
4. Either:
   - Display frames in the console (``output_format="console"``), or
   - Write the ASCII art to a plain-text file (``output_format="file"``), or
   - Re-render the ASCII art back onto video frames and save an .mp4 / .avi
     (``output_format="video"``).
"""

import re
import sys
import time
from typing import Generator, Optional

try:
    import cv2
    from PIL import Image
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "opencv-python, Pillow, and numpy are required: "
        "pip install opencv-python Pillow numpy"
    ) from exc

from config import Config
from image_processor import image_to_ascii

# ANSI escape to clear and reset the terminal cursor to the top-left
_CLEAR = "\033[2J\033[H"


def _cv2_frame_to_pil(frame: np.ndarray) -> "Image.Image":
    """Convert a BGR numpy array (OpenCV frame) to a PIL RGB Image."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def frames_to_ascii(
    video_path: str, config: Optional[Config] = None
) -> Generator[str, None, None]:
    """Yield ASCII art strings for each frame of *video_path*.

    Parameters
    ----------
    video_path:
        Path to the video file.
    config:
        Optional :class:`Config`.

    Yields
    ------
    str
        ASCII art for one video frame.
    """
    if config is None:
        config = Config()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            pil_img = _cv2_frame_to_pil(frame)
            yield image_to_ascii(pil_img, config)
    finally:
        cap.release()


def play_video_in_console(video_path: str, config: Optional[Config] = None) -> None:
    """Stream video as ASCII art directly to the terminal.

    Each frame is printed after clearing the terminal.  Playback speed is
    governed by ``config.fps``.

    Parameters
    ----------
    video_path:
        Path to the video file.
    config:
        Optional :class:`Config`.
    """
    if config is None:
        config = Config()

    frame_delay = 1.0 / config.fps
    for ascii_frame in frames_to_ascii(video_path, config):
        sys.stdout.write(_CLEAR + ascii_frame + "\n")
        sys.stdout.flush()
        time.sleep(frame_delay)


def save_video_as_text(
    video_path: str, output_path: str, config: Optional[Config] = None
) -> None:
    """Write all ASCII frames to a plain-text file separated by form-feeds.

    Parameters
    ----------
    video_path:
        Source video file.
    output_path:
        Destination ``.txt`` file.
    config:
        Optional :class:`Config`.
    """
    if config is None:
        config = Config()

    with open(output_path, "w", encoding="utf-8") as fh:
        for i, ascii_frame in enumerate(frames_to_ascii(video_path, config)):
            if i > 0:
                fh.write("\f\n")  # form-feed as frame separator
            fh.write(ascii_frame + "\n")


def save_video_as_video(
    video_path: str, output_path: str, config: Optional[Config] = None
) -> None:
    """Re-render ASCII frames onto a new video file.

    Each ASCII frame is drawn onto a black image using a monospace font
    embedded via OpenCV, then encoded into an MP4 or AVI file.

    Parameters
    ----------
    video_path:
        Source video file.
    output_path:
        Destination video file (e.g. ``output.mp4``).
    config:
        Optional :class:`Config`.
    """
    if config is None:
        config = Config()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or config.fps
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Determine output codec from extension
    ext = output_path.rsplit(".", 1)[-1].lower()
    fourcc_map = {
        "mp4": "mp4v",
        "avi": "XVID",
        "mov": "mp4v",
    }
    fourcc_str = fourcc_map.get(ext, "mp4v")
    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)

    writer = cv2.VideoWriter(output_path, fourcc, config.fps, (src_w, src_h))

    font_face = cv2.FONT_HERSHEY_PLAIN
    font_scale = 0.6
    font_thickness = 1
    char_h = 10  # approximate character height in pixels

    for ascii_frame in frames_to_ascii(video_path, config):
        canvas = np.zeros((src_h, src_w, 3), dtype=np.uint8)
        for row_idx, line in enumerate(ascii_frame.splitlines()):
            # Strip ANSI codes for video rendering (cv2 can't display them)
            clean_line = _strip_ansi(line)
            y_pos = row_idx * char_h + char_h
            if y_pos > src_h:
                break
            cv2.putText(
                canvas,
                clean_line,
                (0, y_pos),
                font_face,
                font_scale,
                (200, 200, 200),
                font_thickness,
                cv2.LINE_AA,
            )
        writer.write(canvas)

    writer.release()


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from *text*."""
    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    return ansi_escape.sub("", text)
