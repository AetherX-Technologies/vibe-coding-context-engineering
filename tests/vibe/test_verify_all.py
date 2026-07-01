from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from verify_all import build_checks  # noqa: E402


class VerifyAllProfileTests(unittest.TestCase):
    def test_phase1_profile_runs_base_checks_only(self) -> None:
        checks = build_checks(ROOT, "phase1", None)

        self.assertEqual([name for name, _command in checks], ["context", "secrets"])

    def test_full_profile_includes_skill_and_plugin_checks(self) -> None:
        checks = build_checks(ROOT, "full", None)
        names = [name for name, _command in checks]

        self.assertIn("context", names)
        self.assertIn("secrets", names)
        self.assertIn("skill-phase2", names)
        self.assertIn("plugin-phase3", names)

    def test_auto_profile_detects_current_repo_capabilities(self) -> None:
        checks = build_checks(ROOT, "auto", None)
        names = [name for name, _command in checks]

        self.assertIn("skill-phase2", names)
        self.assertIn("plugin-phase3", names)


if __name__ == "__main__":
    unittest.main()
