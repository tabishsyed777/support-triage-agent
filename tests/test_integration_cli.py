import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]


def invoke(path, *options):
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    return subprocess.run(
        [sys.executable, "-m", "support_triage_agent", str(path), *options],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=10,
    )


class CliTests(unittest.TestCase):
    def test_example_reaches_expected_decision(self):
        result = invoke(ROOT / "examples" / "case.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["decision"], {'ticket_id': 'T-204', 'queue': 'identity', 'priority': 'urgent'})
        self.assertEqual([entry["tool"] for entry in report["trace"]],
                         ["read_case", "read_policy", "assess"])

    def test_bad_input_fails_without_report(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for raw in ("{", "[]", "{}"):
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    result = invoke(path)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn("Error:", result.stderr)
                    self.assertEqual(result.stdout, "")

    def test_model_option_requires_key(self):
        result = invoke(ROOT / "examples" / "case.json", "--model", "test-model")
        self.assertEqual(result.returncode, 1)
        self.assertIn("OPENAI_API_KEY", result.stderr)
