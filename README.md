# Codex Any-Node Fork

中文说明: [README_CN.md](./README_CN.md)

A lightweight Windows tool for browsing local Codex Desktop / Codex CLI conversations by working directory and creating a fork from any selectable conversation node. It now includes both an interactive CLI and a graphical GUI.

## Features

- Filter local Codex conversations by the current working directory
- Navigate conversations with the keyboard
- Browse conversations and user messages in a graphical interface
- The GUI uses a modern dark dashboard layout with a status rail, recent workdirs, and split content panels
- Show only user messages as fork candidates
- Create a new branch thread with `fork + rollback`
- Remember selected or used work directories in the GUI and prefer them on the next launch
- Refresh the conversation list manually from the GUI
- Refresh the conversation list automatically when the work directory changes
- Refresh the conversation list automatically after a successful fork

## Requirements

- Windows
- Python 3.10+
- Codex Desktop or Codex CLI installed
- Access to a local Codex sessions directory

This project uses only the Python standard library.

## Quick Start

For first-time setup, beginners can run:

```powershell
.\add_to_user_path.cmd
```


Run:

```powershell
fork -ls
```

Launch the GUI:

```powershell
fork --gui
```

On Windows this path prefers launching the GUI as a detached no-console process.

Or use the dedicated launcher:

```powershell
fork-gui
```

The launcher prefers `pythonw` so the GUI does not keep an extra `cmd` window open.


If the project directory is not in `PATH`, use:

```powershell
.\fork.cmd -ls
```

Or run the script directly:

```powershell
python .\scripts\fork_cli.py -ls
```

Or:

```powershell
python .\scripts\fork_gui.py
```

## Controls

- `↑ / ↓`: move selection
- `Enter`: confirm
- `Backspace`: go back
- `q`: quit

## GUI

- The GUI uses a modern dark card-based layout with a workspace rail and split content panels
- `Workdir` uses an editable dropdown that remembers recently selected or used work directories
- A recent-workdirs list is shown on the left side for one-click switching
- The GUI prefers the last remembered work directory on the next launch
- You can enable “minimize to tray when closing” so the close button hides the window instead of exiting
- `Refresh` button: reload the conversation list for the selected `codex_home` and `workdir`
- Changing `Workdir` triggers an automatic refresh
- `F5`: trigger a manual refresh
- Double-click a user message or use `Fork Selected Turn` to create a fork
- After a successful fork, the GUI refreshes the conversation list automatically

After entering a conversation, the tool shows only user messages.
Once a target message is selected, it creates a new thread and rolls that new thread back to the matching turn.

## Simplified Flow

```mermaid
flowchart TD
    A["Run `fork -ls`"] --> B["Scan local conversations for the current working directory"]
    B --> C["Select a conversation"]
    C --> D["List only user messages in that conversation"]
    D --> E["Select a target user message"]
    E --> F["Confirm fork target"]
    F --> G["Read the source thread and locate the target turn"]
    G --> H["Run `thread/fork` to create a new thread"]
    H --> I["Run `thread/rollback` on the new thread"]
    I --> J["Verify the last turn of the new thread"]
    J --> K["Fork completed"]
```

## Project Structure

```text
.
├─ add_to_user_path.cmd
├─ fork.cmd
├─ fork-gui.cmd
├─ LICENSE
├─ README.md
├─ README_CN.md
└─ scripts
   ├─ fork_cli.py
   ├─ fork_gui.py
   └─ session_tool.py
```

## Notes

- The original thread is never modified
- Rollback is applied only to the new thread
- After a fork, the tool attempts to load the new thread into Codex automatically via `thread/resume`
- If Codex Desktop is running, the tool also restarts the app to refresh the thread list
- If the new thread still does not appear, reopen Codex manually

## License

Licensed under the MIT License.
