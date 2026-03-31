import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from utils.argumentos import CLIArgumentParser  # noqa: E402


class CliArgumentParserTests(unittest.TestCase):
    def parse(self, *argv):
        parser = CLIArgumentParser()
        with patch.object(sys, "argv", ["chat", *argv]):
            return parser.parse_args()

    def test_anthropic_alias_maps_to_claude(self):
        args = self.parse("--anthropic", "teste")

        self.assertEqual(args.provider, "claude")

    def test_provider_anthropic_is_normalized_to_claude(self):
        args = self.parse("--provider", "anthropic", "teste")

        self.assertEqual(args.provider, "claude")

    def test_persistent_requires_openai_provider(self):
        parser = CLIArgumentParser()
        with patch.object(sys, "argv", ["chat", "--claude", "--persistent", "yes", "teste"]):
            with self.assertRaises(SystemExit):
                parser.parse_args()


if __name__ == "__main__":
    unittest.main()
