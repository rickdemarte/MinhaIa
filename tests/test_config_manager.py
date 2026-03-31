import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from config.manager import ConfigManager  # noqa: E402


def build_args(**overrides):
    base = {
        "transcribe": False,
        "fast": False,
        "cheap": False,
        "smart": False,
        "smartest": False,
        "absurdo": False,
        "model": None,
        "max_tokens": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class ConfigManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = ConfigManager()

    def test_normalize_provider_aliases(self):
        self.assertEqual(self.manager.normalize_provider("kimi"), "moonshot")
        self.assertEqual(self.manager.normalize_provider("anthropic"), "claude")

    def test_openai_default_uses_current_primary_model(self):
        model, max_tokens, is_o_model, temperature = self.manager.get_model_config(
            build_args(),
            "openai",
        )

        self.assertEqual(model, "gpt-5.4")
        self.assertEqual(max_tokens, 65536)
        self.assertFalse(is_o_model)
        self.assertEqual(temperature, 0.7)

    def test_openai_absurdo_uses_pro_model(self):
        model, _, is_o_model, _ = self.manager.get_model_config(
            build_args(absurdo=True),
            "openai",
        )

        self.assertEqual(model, "gpt-5.4-pro")
        self.assertFalse(is_o_model)

    def test_custom_model_preserves_explicit_override(self):
        model, max_tokens, is_o_model, temperature = self.manager.get_model_config(
            build_args(model="custom-model"),
            "openai",
        )

        self.assertEqual(model, "custom-model")
        self.assertEqual(max_tokens, 4096)
        self.assertFalse(is_o_model)
        self.assertEqual(temperature, 0.7)

    def test_gemini_default_uses_sdk_style_model_id(self):
        model, _, _, _ = self.manager.get_model_config(
            build_args(),
            "gemini",
        )

        self.assertEqual(model, "gemini-2.5-flash")
        self.assertFalse(model.startswith("models/"))


if __name__ == "__main__":
    unittest.main()
