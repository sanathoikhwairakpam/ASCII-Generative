# ASCII-Generative

A comprehensive Python program for generating ASCII art from text, images, and videos.

---

## Features

- **Text → ASCII** – render any word or phrase as an ASCII art banner using [pyfiglet](https://github.com/pwaller/pyfiglet), with support for dozens of font styles.
- **Random words** – pick random words from a built-in list and render them instantly.
- **Image → ASCII** – convert any image file (PNG, JPEG, …) to ASCII art using Pillow.
- **Video → ASCII** – convert video files frame-by-frame to ASCII art using OpenCV, with three output modes:
  - Live playback in the terminal
  - Plain-text file export
  - Re-rendered ASCII video file (MP4/AVI)
- **Customisation** – choose character sets, scale, width, contrast, brightness, colour output (ANSI), and background colour.
- **Modular** – each component (`config`, `text_generator`, `image_processor`, `video_processor`) can be imported and used as a library.

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `pyfiglet`, `Pillow`, `opencv-python`, `numpy`.

---

## Quick Start

### Text to ASCII

```bash
# Specific word
python main.py text --word "Hello"

# Random word
python main.py text --random

# Three random words with the "big" font and colour
python main.py text --random --random-count 3 --font big --color

# Slanted font, saved to a file
python main.py text --word "Python" --font slant --output-format file --output art.txt

# List all available fonts
python main.py text --list-fonts
```

### Image to ASCII

```bash
# Basic conversion (prints to console)
python main.py image photo.jpg

# Wider output, detailed character set, coloured
python main.py image photo.jpg --width 120 --char-set detailed --color

# Save to file
python main.py image photo.jpg --output-format file --output photo_ascii.txt
```

### Video to ASCII

```bash
# Live ASCII playback in the terminal at 15 fps
python main.py video clip.mp4 --fps 15

# Save each frame to a text file (frames separated by form-feed)
python main.py video clip.mp4 --output-format file --output clip_ascii.txt

# Re-render as an ASCII art video file
python main.py video clip.mp4 --output-format video --output clip_ascii.mp4 --fps 10
```

---

## Customisation Options

| Flag | Default | Description |
|------|---------|-------------|
| `--char-set` | `standard` | Character set: `standard`, `detailed`, `minimal`, `blocks`, `binary`, `symbols`, or `custom` |
| `--custom-chars` | – | Custom character string (use with `--char-set custom`) |
| `--scale` | `0.4` | Downsample factor for images/videos (0 < scale ≤ 1) |
| `--width` | – | Force output width in characters (overrides `--scale`) |
| `--color` | off | Enable 24-bit ANSI colour output |
| `--contrast` | `1.0` | Contrast multiplier |
| `--brightness` | `0.0` | Brightness offset (−255 to 255) |
| `--bg-color` | – | ANSI background colour (e.g. `black`, `blue`) |
| `--output-format` | `console` | Output destination: `console`, `file`, or `video` |
| `--output` | – | Output file path (required for `file` / `video` formats) |
| `--fps` | `10` | Frames per second for video playback/export *(video only)* |
| `--font` | `standard` | Pyfiglet font name *(text only)* |

---

## Project Structure

```
ASCII-Generative/
├── main.py             # CLI entry point
├── config.py           # Centralised configuration dataclass
├── text_generator.py   # Text → ASCII using pyfiglet
├── image_processor.py  # Image → ASCII using Pillow + NumPy
├── video_processor.py  # Video → ASCII using OpenCV
├── tests.py            # Unit tests (36 tests)
└── requirements.txt    # Python dependencies
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests.py -v
```

---

## Using as a Library

```python
from config import Config
from text_generator import text_to_ascii, random_word
from image_processor import image_to_ascii
from PIL import Image

# Text art
cfg = Config(font="slant", color=True)
print(text_to_ascii("Hello", cfg))

# Random word
words = random_word(3)
for w in words:
    print(text_to_ascii(w))

# Image art
img = Image.open("photo.jpg")
cfg = Config(scale=0.3, char_set="detailed")
print(image_to_ascii(img, cfg))
```