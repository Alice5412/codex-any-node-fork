#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import time


def find_codex_desktop_app_id() -> str:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-StartApps | "
                "Where-Object { $_.AppID -like 'OpenAI.Codex_*' } | "
                "Select-Object -First 1 -ExpandProperty AppID"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=creationflags,
        check=False,
    )
    return result.stdout.strip()


def build_desktop_launch_command(executable_path: str, app_id: str) -> list[str]:
    if app_id:
        return ["explorer.exe", f"shell:AppsFolder\\{app_id}"]
    return [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Start-Process -FilePath '{executable_path}'",
    ]


def find_running_codex_desktop_executable() -> str:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Get-CimInstance Win32_Process | "
                "Where-Object { "
                "$_.Name -eq 'Codex.exe' -and "
                "$_.ExecutablePath -like '*Codex.exe' -and "
                "$_.ExecutablePath -notlike '*\\resources\\codex.exe' -and "
                "$_.CommandLine -notlike '*--type=*' "
                "} | "
                "Select-Object -First 1 -ExpandProperty ExecutablePath"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=creationflags,
        check=False,
    )
    return result.stdout.strip()


def restart_codex_desktop_app() -> tuple[str, str]:
    executable_path = find_running_codex_desktop_executable()
    app_id = find_codex_desktop_app_id()
    if not executable_path:
        return "not_running", ""

    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    f"$exe = '{executable_path}'; "
                    "Get-CimInstance Win32_Process | "
                    "Where-Object { $_.ExecutablePath -eq $exe } | "
                    "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
                ),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            check=False,
        )
        time.sleep(1.5)
        subprocess.run(
            build_desktop_launch_command(executable_path, app_id),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            check=False,
        )
        return "restarted", ""
    except Exception as exc:  # noqa: BLE001
        return "failed", str(exc)
