@echo off
setlocal

set "PYTHONW_EXE=%~dp0.venv\Scripts\pythonw.exe"
if not exist "%PYTHONW_EXE%" set "PYTHONW_EXE="

if not defined PYTHONW_EXE (
  for %%I in (python.exe) do set "PYTHON_EXE=%%~$PATH:I"
  if defined PYTHON_EXE (
    set "PYTHONW_EXE=%PYTHON_EXE:python.exe=pythonw.exe%"
    if not exist "%PYTHONW_EXE%" set "PYTHONW_EXE="
  )
)

if not defined PYTHONW_EXE (
  for %%I in (pythonw.exe) do set "PYTHONW_EXE=%%~$PATH:I"
)

if not defined PYTHONW_EXE (
  echo Could not locate pythonw.exe.>&2
  exit /b 1
)

start "" "%PYTHONW_EXE%" "%~dp0scripts\webui_tray.py" %*
exit /b 0
