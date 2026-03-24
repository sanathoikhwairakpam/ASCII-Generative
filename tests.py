"""
tests.py - Unit tests for the ASCII art generator modules.

Run with:  python -m pytest tests.py -v
       or: python tests.py
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config, CHAR_SETS, FONT_PRESETS
from text_generator import text_to_ascii, random_word, list_fonts
from image_processor import image_to_ascii


# ---------------------------------------------------------------------------
# config.py tests
# ---------------------------------------------------------------------------

class TestConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = Config()
        self.assertEqual(cfg.char_set, "standard")
        self.assertEqual(cfg.font, "standard")
        self.assertAlmostEqual(cfg.scale, 0.4)
        self.assertFalse(cfg.color)

    def test_get_char_set_named(self):
        for name in CHAR_SETS:
            cfg = Config(char_set=name)
            self.assertEqual(cfg.get_char_set(), CHAR_SETS[name])

    def test_get_char_set_custom(self):
        custom = "#@. "
        cfg = Config(char_set=custom)
        self.assertEqual(cfg.get_char_set(), custom)

    def test_validate_ok(self):
        cfg = Config(scale=0.5, contrast=1.2, fps=24.0, output_format="console")
        cfg.validate()  # Should not raise

    def test_validate_bad_scale(self):
        with self.assertRaises(ValueError):
            Config(scale=0).validate()
        with self.assertRaises(ValueError):
            Config(scale=1.5).validate()

    def test_validate_bad_contrast(self):
        with self.assertRaises(ValueError):
            Config(contrast=0).validate()

    def test_validate_bad_fps(self):
        with self.assertRaises(ValueError):
            Config(fps=0).validate()

    def test_validate_bad_output_format(self):
        with self.assertRaises(ValueError):
            Config(output_format="gif").validate()

    def test_validate_missing_output_path(self):
        with self.assertRaises(ValueError):
            Config(output_format="file", output_path=None).validate()
        with self.assertRaises(ValueError):
            Config(output_format="video", output_path=None).validate()


# ---------------------------------------------------------------------------
# text_generator.py tests
# ---------------------------------------------------------------------------

class TestTextGenerator(unittest.TestCase):
    def test_text_to_ascii_returns_string(self):
        result = text_to_ascii("hello")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_text_to_ascii_contains_characters(self):
        result = text_to_ascii("ABC")
        # The result should be non-empty multi-line text
        self.assertIn("\n", result)

    def test_text_to_ascii_custom_font(self):
        cfg = Config(font="banner")
        result = text_to_ascii("hi", cfg)
        self.assertIsInstance(result, str)

    def test_text_to_ascii_color(self):
        cfg = Config(color=True)
        result = text_to_ascii("ok", cfg)
        # ANSI codes should be present
        self.assertIn("\033[", result)

    def test_random_word_count(self):
        words = random_word(5)
        self.assertEqual(len(words), 5)

    def test_random_word_default(self):
        words = random_word()
        self.assertEqual(len(words), 1)

    def test_random_word_zero(self):
        words = random_word(0)
        self.assertEqual(words, [])

    def test_random_word_types(self):
        words = random_word(10)
        for w in words:
            self.assertIsInstance(w, str)
            self.assertGreater(len(w), 0)

    def test_list_fonts_returns_list(self):
        fonts = list_fonts()
        self.assertIsInstance(fonts, list)
        self.assertIn("standard", fonts)
        self.assertGreater(len(fonts), 10)


# ---------------------------------------------------------------------------
# image_processor.py tests
# ---------------------------------------------------------------------------

class TestImageProcessor(unittest.TestCase):
    def _make_test_image(self, width=80, height=40, mode="RGB"):
        """Create a simple PIL test image."""
        from PIL import Image
        img = Image.new(mode, (width, height), color=128)
        return img

    def test_image_to_ascii_basic(self):
        img = self._make_test_image()
        result = image_to_ascii(img)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_image_to_ascii_has_newlines(self):
        img = self._make_test_image()
        result = image_to_ascii(img)
        lines = result.splitlines()
        self.assertGreater(len(lines), 1)

    def test_image_to_ascii_scale(self):
        img = self._make_test_image(width=200, height=100)
        cfg_small = Config(scale=0.1)
        cfg_large = Config(scale=0.5)
        small_result = image_to_ascii(img, cfg_small)
        large_result = image_to_ascii(img, cfg_large)
        self.assertLess(len(small_result), len(large_result))

    def test_image_to_ascii_width_override(self):
        img = self._make_test_image(width=200, height=100)
        cfg = Config(width=40)
        result = image_to_ascii(img, cfg)
        lines = result.splitlines()
        # Each line should be at most 40 characters (ignoring ANSI codes)
        for line in lines:
            self.assertLessEqual(len(line), 40)

    def test_image_to_ascii_custom_char_set(self):
        img = self._make_test_image()
        cfg = Config(char_set="minimal")
        result = image_to_ascii(img, cfg)
        self.assertIsInstance(result, str)

    def test_image_to_ascii_color(self):
        img = self._make_test_image()
        cfg = Config(color=True, scale=0.1)
        result = image_to_ascii(img, cfg)
        self.assertIn("\033[", result)

    def test_image_to_ascii_contrast(self):
        img = self._make_test_image()
        cfg = Config(contrast=2.0)
        result = image_to_ascii(img, cfg)
        self.assertIsInstance(result, str)

    def test_image_to_ascii_brightness(self):
        img = self._make_test_image()
        cfg = Config(brightness=50.0)
        result = image_to_ascii(img, cfg)
        self.assertIsInstance(result, str)

    def test_image_to_ascii_grayscale_input(self):
        from PIL import Image
        img = Image.new("L", (50, 25), color=100)
        result = image_to_ascii(img)
        self.assertIsInstance(result, str)

    def test_all_char_sets(self):
        img = self._make_test_image()
        for name in CHAR_SETS:
            cfg = Config(char_set=name)
            result = image_to_ascii(img, cfg)
            self.assertIsInstance(result, str, f"Failed for char_set={name}")


# ---------------------------------------------------------------------------
# CLI tests (via argparse)
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):
    def _run_main(self, args):
        """Run main() with patched sys.argv; capture stdout."""
        import io
        from contextlib import redirect_stdout
        from main import build_parser

        parser = build_parser()
        parsed = parser.parse_args(args)
        buf = io.StringIO()
        with redirect_stdout(buf):
            parsed.func(parsed)
        return buf.getvalue()

    def test_cli_text_word(self):
        output = self._run_main(["text", "--word", "test"])
        self.assertGreater(len(output), 0)

    def test_cli_text_random(self):
        output = self._run_main(["text", "--random"])
        self.assertGreater(len(output), 0)

    def test_cli_text_random_count(self):
        output = self._run_main(["text", "--random", "--random-count", "3"])
        self.assertGreater(len(output), 0)

    def test_cli_text_font(self):
        output = self._run_main(["text", "--word", "hi", "--font", "banner"])
        self.assertGreater(len(output), 0)

    def test_cli_text_color(self):
        output = self._run_main(["text", "--word", "hi", "--color"])
        self.assertIn("\033[", output)

    def test_cli_text_list_fonts(self):
        output = self._run_main(["text", "--list-fonts"])
        self.assertIn("standard", output)

    def test_cli_image(self):
        from PIL import Image
        import tempfile
        import os
        img = Image.new("RGB", (50, 25), color=200)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp_path = f.name
        try:
            img.save(tmp_path)
            output = self._run_main(["image", tmp_path, "--scale", "0.2"])
            self.assertGreater(len(output), 0)
        finally:
            os.unlink(tmp_path)

    def test_cli_file_output(self):
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w"
        ) as f:
            tmp_path = f.name
        os.unlink(tmp_path)  # let main.py create it
        try:
            self._run_main(
                ["text", "--word", "save", "--output-format", "file",
                 "--output", tmp_path]
            )
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path) as fh:
                content = fh.read()
            self.assertGreater(len(content), 0)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
