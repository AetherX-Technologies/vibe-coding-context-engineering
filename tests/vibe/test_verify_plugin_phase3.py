from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/vibe"))

from verify_plugin_phase3 import (  # noqa: E402
    iter_hook_commands,
    verify_manifest_contract,
    verify_plugin_hooks_fail_open_without_scaffold,
)


VALID_MANIFEST = {
    "name": "vibe-coding",
    "version": "0.1.0",
    "description": "Reusable workflow plugin.",
    "author": {"name": "Vibe Coding Context Engineering"},
    "interface": {
        "displayName": "Vibe Coding",
        "shortDescription": "Short description.",
        "longDescription": "Long description.",
        "developerName": "Vibe Coding Context Engineering",
        "category": "Productivity",
        "capabilities": ["Skills", "Hooks"],
        "defaultPrompt": ["Run verification."],
    },
}


class PluginManifestContractTests(unittest.TestCase):
    def test_valid_manifest_contract_passes(self) -> None:
        errors: list[str] = []

        verify_manifest_contract(VALID_MANIFEST, errors)

        self.assertEqual(errors, [])

    def test_missing_developer_name_fails(self) -> None:
        manifest = {
            **VALID_MANIFEST,
            "interface": {**VALID_MANIFEST["interface"], "developerName": ""},
        }
        errors: list[str] = []

        verify_manifest_contract(manifest, errors)

        self.assertIn("plugin.json interface.developerName must be a non-empty string", errors)

    def test_capabilities_must_be_non_empty_strings(self) -> None:
        manifest = {
            **VALID_MANIFEST,
            "interface": {**VALID_MANIFEST["interface"], "capabilities": ["Skills", ""]},
        }
        errors: list[str] = []

        verify_manifest_contract(manifest, errors)

        self.assertIn("plugin.json interface.capabilities must be an array of non-empty strings", errors)


class PluginHookContractTests(unittest.TestCase):
    def test_iter_hook_commands_extracts_nested_commands(self) -> None:
        hooks = {
            "hooks": {
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {"type": "command", "command": "true"},
                            {"type": "prompt", "prompt": "ignored"},
                        ]
                    }
                ]
            }
        }

        self.assertEqual(iter_hook_commands(hooks), ["true"])

    def test_plugin_hooks_must_fail_open_without_project_scaffold(self) -> None:
        hooks = {
            "hooks": {
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "sh -lc 'SCRIPT=\"$PWD/.codex/hooks/missing.py\"; if [ ! -f \"$SCRIPT\" ]; then exit 0; fi; /usr/bin/python3 \"$SCRIPT\"'",
                            }
                        ]
                    }
                ]
            }
        }
        errors: list[str] = []

        verify_plugin_hooks_fail_open_without_scaffold(hooks, errors)

        self.assertEqual(errors, [])

    def test_plugin_hooks_report_missing_script_failures(self) -> None:
        hooks = {
            "hooks": {
                "UserPromptSubmit": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "sh -lc '/usr/bin/python3 \"$PWD/.codex/hooks/missing.py\"'",
                            }
                        ]
                    }
                ]
            }
        }
        errors: list[str] = []

        verify_plugin_hooks_fail_open_without_scaffold(hooks, errors)

        self.assertEqual(len(errors), 1)
        self.assertIn("must exit 0 when project scaffold scripts are absent", errors[0])


if __name__ == "__main__":
    unittest.main()
