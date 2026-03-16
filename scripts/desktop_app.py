#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import time


MAIN_PROCESS_FILTER = (
    "Get-CimInstance Win32_Process | "
    "Where-Object { "
    "$_.Name -eq 'Codex.exe' -and "
    "$_.ExecutablePath -like '*Codex.exe' -and "
    "$_.ExecutablePath -notlike '*\\resources\\codex.exe' -and "
    "$_.CommandLine -notlike '*--type=*' "
    "}"
)


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run_powershell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        creationflags=_creationflags(),
        check=False,
    )


def _quote_powershell(value: str) -> str:
    return value.replace("'", "''")


def list_running_codex_desktop_process_ids(executable_path: str = "") -> list[int]:
    command = MAIN_PROCESS_FILTER
    if executable_path:
        quoted = _quote_powershell(executable_path)
        command += f" | Where-Object {{ $_.ExecutablePath -eq '{quoted}' }}"
    command += " | Select-Object -ExpandProperty ProcessId"
    result = _run_powershell(command)
    process_ids: list[int] = []
    for line in result.stdout.splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            process_ids.append(int(text))
        except ValueError:
            continue
    return process_ids


def wait_for_codex_desktop_state(
    *,
    executable_path: str,
    should_exist: bool,
    previous_ids: set[int] | None = None,
    timeout_seconds: float = 15.0,
) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        running_ids = set(list_running_codex_desktop_process_ids(executable_path))
        if should_exist:
            if previous_ids is None:
                if running_ids:
                    return True
            elif running_ids - previous_ids:
                return True
        elif not running_ids:
            return True
        time.sleep(0.25)
    return False


def stop_codex_desktop_processes(executable_path: str) -> None:
    quoted = _quote_powershell(executable_path)
    _run_powershell(
        (
            f"$exe = '{quoted}'; "
            "Get-CimInstance Win32_Process | "
            "Where-Object { $_.ExecutablePath -eq $exe } | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
        )
    )


def build_desktop_launch_commands(executable_path: str, app_id: str) -> list[list[str]]:
    commands: list[list[str]] = []
    if app_id:
        commands.append(["cmd.exe", "/c", f'start "" "shell:AppsFolder\\{app_id}"'])
        commands.append(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
    if executable_path:
        commands.append([executable_path])
    return commands


def find_codex_desktop_app_id() -> str:
    result = _run_powershell(
        (
            "Get-StartApps | "
            "Where-Object { $_.AppID -like 'OpenAI.Codex_*' } | "
            "Select-Object -First 1 -ExpandProperty AppID"
        )
    )
    return result.stdout.strip()


def build_desktop_launch_command(executable_path: str, app_id: str) -> list[str]:
    commands = build_desktop_launch_commands(executable_path, app_id)
    return commands[0] if commands else []


def find_running_codex_desktop_executable() -> str:
    result = _run_powershell(
        MAIN_PROCESS_FILTER + " | Select-Object -First 1 -ExpandProperty ExecutablePath"
    )
    return result.stdout.strip()


def restart_codex_desktop_app() -> tuple[str, str]:
    executable_path = find_running_codex_desktop_executable()
    app_id = find_codex_desktop_app_id()
    if not executable_path:
        return "not_running", ""

    try:
        previous_ids = set(list_running_codex_desktop_process_ids(executable_path))
        stop_codex_desktop_processes(executable_path)
        if not wait_for_codex_desktop_state(
            executable_path=executable_path,
            should_exist=False,
            timeout_seconds=20.0,
        ):
            return "failed", "Timed out while waiting for Codex App to exit."

        for launch_command in build_desktop_launch_commands(executable_path, app_id):
            try:
                subprocess.Popen(
                    launch_command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=_creationflags(),
                )
            except OSError:
                continue

            if wait_for_codex_desktop_state(
                executable_path=executable_path,
                should_exist=True,
                previous_ids=previous_ids,
                timeout_seconds=20.0,
            ):
                return "restarted", ""

        return "failed", "Codex App stop succeeded, but automatic relaunch did not start a new main process."
    except Exception as exc:  # noqa: BLE001
        return "failed", str(exc)