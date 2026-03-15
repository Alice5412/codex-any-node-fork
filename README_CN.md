# Codex Any-Node Fork

English version: [README.md](./README.md)

一个面向 Windows 的轻量工具，用于按当前工作目录浏览本地 Codex Desktop / Codex CLI 对话，并从任意可选对话节点创建分支线程。现在同时提供交互式 CLI 和可视化 GUI。

## 功能

- 按当前工作目录筛选本地 Codex 对话
- 使用上下键选择目标对话
- 提供可视化 GUI 浏览对话和用户消息
- GUI 采用深色仪表盘式布局，包含侧边状态区、最近工作目录和双列表内容区
- 仅展示对话中的用户消息作为分支基准
- 对目标线程执行 `fork + rollback`
- GUI 会记住选中过或操作过的工作目录，并在下次启动时优先使用
- GUI 中可手动刷新会话列表
- GUI 中切换工作目录后会自动刷新
- 分支成功后 GUI 会自动刷新列表

## 要求

- Windows
- Python 3.10+
- 已安装 Codex Desktop / Codex CLI
- 本地存在可访问的 Codex 会话目录

本项目只使用 Python 标准库。

## 快速开始

第一次使用时，可以先运行：

```powershell
.\add_to_user_path.cmd
```

直接运行：

```powershell
fork -ls
```

启动 GUI：

```powershell
fork --gui
```

在 Windows 下，该入口会优先以无控制台窗口的方式分离启动 GUI。

或者直接使用专用启动器：

```powershell
fork-gui
```

该启动器会优先使用 `pythonw`，避免额外停留一个 `cmd` 终端窗口。

如果项目目录还没有加入 `PATH`，可以先这样运行：

```powershell
.\fork.cmd -ls
```

或者：

```powershell
python .\scripts\fork_cli.py -ls
```

也可以直接运行 GUI 脚本：

```powershell
python .\scripts\fork_gui.py
```

## 交互方式

- `↑ / ↓`：切换选项
- `Enter`：确认
- `Backspace`：返回上一级
- `q`：退出

## GUI

- GUI 采用现代化深色卡片布局，工作目录状态、最近记录和操作区分层展示
- `Workdir` 使用可输入的下拉框，会记住最近选中过或执行过操作的工作目录
- 左侧会显示最近工作目录列表，点击即可切换
- 下次启动 GUI 时，会优先使用上次记住的工作目录
- 可以勾选“关闭时最小化到系统托盘”，关闭窗口时不直接退出
- `Refresh` 按钮：按当前 `codex_home` 和 `workdir` 重新加载会话列表
- 切换 `Workdir` 后会自动刷新列表
- `F5`：手动刷新列表
- 双击用户消息，或点击 `Fork Selected Turn` 执行分支
- 分支成功后，GUI 会自动刷新会话列表

进入某个对话后，程序只显示用户消息。
选定目标消息后，会创建一个新线程，并将新线程回滚到该消息对应的 turn。

## 简化流程

```mermaid
flowchart TD
    A["运行 `fork -ls`"] --> B["按当前工作目录扫描本地对话"]
    B --> C["上下键选择目标对话"]
    C --> D["只列出该对话中的用户消息"]
    D --> E["上下键选择目标用户消息"]
    E --> F["确认分支位置"]
    F --> G["读取原线程并定位目标 turn"]
    G --> H["执行 `thread/fork` 创建新线程"]
    H --> I["对新线程执行 `thread/rollback`"]
    I --> J["校验新线程最后一个 turn"]
    J --> K["完成分支"]
```

## 项目结构

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

## 说明

- 不会修改原线程
- 只会对新创建的线程执行 rollback
- fork 完成后，工具会先尝试通过 `thread/resume` 自动把新线程加载进 Codex
- 如果 Codex Desktop 正在运行，工具还会自动重启 App 来刷新线程列表
- 如果新线程仍然没有显示出来，再手动重新打开 Codex

## License

Licensed under the MIT License.
