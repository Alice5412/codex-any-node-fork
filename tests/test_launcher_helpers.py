import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from desktop_app import build_desktop_launch_command  # noqa: E402
from fork_cli import resolve_codex_command_args  # noqa: E402


class LauncherHelperTests(unittest.TestCase):
    def test_build_desktop_launch_command_prefers_app_id(self) -> None:
        command = build_desktop_launch_command(
            r"C:\Program Files\WindowsApps\OpenAI.Codex\app\Codex.exe",
            "OpenAI.Codex_2p2nqsd0c76g0!App",
        )
        self.assertEqual(
            command,
            ["explorer.exe", r"shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"],
        )

    def test_resolve_codex_command_args_prefers_node_wrapper_for_cmd(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            npm_root = root / "npm"
            wrapper = npm_root / "codex.cmd"
            wrapper.parent.mkdir(parents=True, exist_ok=True)
            wrapper.write_text("@echo off\n", encoding="utf-8")
            (npm_root / "node.exe").write_text("", encoding="utf-8")
            js_path = npm_root / "node_modules" / "@openai" / "codex" / "bin" / "codex.js"
            js_path.parent.mkdir(parents=True, exist_ok=True)
            js_path.write_text("console.log('codex');\n", encoding="utf-8")

            command = resolve_codex_command_args(str(wrapper))

            self.assertEqual(command, [str(npm_root / "node.exe"), str(js_path)])

    def test_resolve_codex_command_args_wraps_js_with_node(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            npm_root = root / "npm"
            npm_root.mkdir(parents=True, exist_ok=True)
            (npm_root / "node.exe").write_text("", encoding="utf-8")
            js_path = npm_root / "node_modules" / "@openai" / "codex" / "bin" / "codex.js"
            js_path.parent.mkdir(parents=True, exist_ok=True)
            js_path.write_text("console.log('codex');\n", encoding="utf-8")

            command = resolve_codex_command_args(str(js_path))

            self.assertEqual(command, [str(npm_root / "node.exe"), str(js_path)])


if __name__ == "__main__":
    unittest.main()
