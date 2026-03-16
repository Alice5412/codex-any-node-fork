#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import os
import tempfile
import traceback
from pathlib import Path

DEFAULT_CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
LOG_PATH = Path(tempfile.gettempdir()) / "codex-session-toolkit-tray.log"
APP_NAME = "Codex Session Toolkit"


def log_line(message: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(message.rstrip() + "\n")
    except OSError:
        pass


def show_error_dialog(message: str) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, message, APP_NAME, 0x00000010)
    except Exception:
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch Codex Session Toolkit Web UI in the system tray")
    parser.add_argument("--codex-home", type=Path, default=DEFAULT_CODEX_HOME, help="Codex home directory")
    parser.add_argument("--workdir", type=Path, help="Target working directory; defaults to current directory")
    parser.add_argument("--accounts-root", type=Path, help="Directory containing one subdirectory per switchable account")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address used by the local Web UI server")
    parser.add_argument("--port", type=int, default=8765, help="Port used by the local Web UI server; use 0 for an automatic port")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser when launching the local Web UI")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    codex_home = args.codex_home.expanduser().resolve()
    workdir = args.workdir.expanduser().resolve() if args.workdir is not None else None
    accounts_root = args.accounts_root.expanduser().resolve() if args.accounts_root is not None else None
    log_line("startup")
    log_line(f"codex_home={codex_home}")
    log_line(f"workdir={workdir}")
    log_line(f"accounts_root={accounts_root}")

    try:
        from webui.tray_app import run_webui_tray_app

        return run_webui_tray_app(
            codex_home=codex_home,
            initial_workdir=workdir,
            accounts_root=accounts_root,
            host=args.host,
            port=args.port,
            open_browser=not args.no_browser,
        )
    except Exception as exc:  # noqa: BLE001
        log_line("startup_failed")
        log_line(traceback.format_exc())
        show_error_dialog(f"Failed to start the background Web UI.\n\n{exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
