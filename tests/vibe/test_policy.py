from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from policy import (  # noqa: E402
    bash_policy,
    changed_files,
    fingerprint_files,
    scan_text_for_secrets,
)


class BashPolicyTests(unittest.TestCase):
    def test_blocks_destructive_remove_root(self) -> None:
        decision, reason = bash_policy("rm -rf /")

        self.assertEqual(decision, "deny")
        self.assertIn("Destructive command blocked", reason)

    def test_allows_rtk_commands(self) -> None:
        decision, reason = bash_policy("rtk test python3 scripts/vibe/verify_all.py --root .")

        self.assertEqual(decision, "allow")
        self.assertEqual(reason, "")

    def test_warns_for_plain_git_commands(self) -> None:
        decision, reason = bash_policy("git status --short")

        self.assertEqual(decision, "warn")
        self.assertIn("rtk", reason)


class SecretScanTests(unittest.TestCase):
    def test_detects_high_signal_secret(self) -> None:
        findings = scan_text_for_secrets("config.py", 'OPENAI_API_KEY = "sk-' + "a" * 30 + '"')

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].name, "OpenAI key")

    def test_allows_marked_secret_examples(self) -> None:
        findings = scan_text_for_secrets(
            "docs/examples/example.md",
            'OPENAI_API_KEY = "sk-' + "a" * 30 + '" # vibe-allow-secret-example',
        )

        self.assertEqual(findings, [])


class FingerprintTests(unittest.TestCase):
    def test_changed_files_ignores_verification_records_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".context").mkdir()
            (root / ".context/verification.jsonl").write_text("{}", encoding="utf-8")
            (root / "AGENTS.md").write_text("instructions", encoding="utf-8")

            files = changed_files(root)

            self.assertIn("AGENTS.md", files)
            self.assertNotIn(".context/verification.jsonl", files)

    def test_fingerprint_changes_for_tracked_text_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "AGENTS.md"
            path.write_text("a", encoding="utf-8")
            first = fingerprint_files(root, ["AGENTS.md"])
            path.write_text("b", encoding="utf-8")
            second = fingerprint_files(root, ["AGENTS.md"])

            self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
