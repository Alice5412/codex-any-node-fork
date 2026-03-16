from __future__ import annotations

import ctypes
import os
import tempfile
import threading
import webbrowser
from ctypes import wintypes
from pathlib import Path

from .server import create_webui_server


APP_NAME = "Codex Session Toolkit"
LOG_PATH = Path(tempfile.gettempdir()) / "codex-session-toolkit-tray.log"
OPEN_WEB_UI_COMMAND = 1001
EXIT_COMMAND = 1002
TRAY_ICON_UID = 1

WM_COMMAND = 0x0111
WM_DESTROY = 0x0002
WM_NULL = 0x0000
WM_USER = 0x0400
WM_CONTEXTMENU = 0x007B
WM_LBUTTONDBLCLK = 0x0203
WM_LBUTTONUP = 0x0202
WM_RBUTTONUP = 0x0205

TRAY_CALLBACK_MESSAGE = WM_USER + 20

MF_SEPARATOR = 0x0800
MF_STRING = 0x0000
NIF_ICON = 0x00000002
NIF_MESSAGE = 0x00000001
NIF_TIP = 0x00000004
NIM_ADD = 0x00000000
NIM_DELETE = 0x00000002
TPM_BOTTOMALIGN = 0x0020
TPM_LEFTALIGN = 0x0000
TPM_RIGHTBUTTON = 0x0002
TPM_RETURNCMD = 0x0100

IDI_APPLICATION = 32512
IMAGE_ICON = 1
LR_DEFAULTSIZE = 0x00000040
LR_LOADFROMFILE = 0x00000010

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

LRESULT = ctypes.c_ssize_t
UINT_PTR = ctypes.c_size_t
LPCRECT = ctypes.POINTER(wintypes.RECT)
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
        ("lPrivate", wintypes.DWORD),
    ]


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HANDLE),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uTimeoutOrVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
    ]


user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.DestroyWindow.restype = wintypes.BOOL
user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.LoadImageW.restype = wintypes.HANDLE
user32.LoadIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR]
user32.LoadIconW.restype = wintypes.HANDLE
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, UINT_PTR, wintypes.LPCWSTR]
user32.AppendMenuW.restype = wintypes.BOOL
user32.DestroyMenu.argtypes = [wintypes.HMENU]
user32.DestroyMenu.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
user32.GetCursorPos.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, LPCRECT]
user32.TrackPopupMenu.restype = wintypes.UINT
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostMessageW.restype = wintypes.BOOL
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.restype = LRESULT
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.DestroyIcon.argtypes = [wintypes.HANDLE]
user32.DestroyIcon.restype = wintypes.BOOL
user32.UnregisterClassW.argtypes = [wintypes.LPCWSTR, wintypes.HINSTANCE]
user32.UnregisterClassW.restype = wintypes.BOOL
shell32.Shell_NotifyIconW.argtypes = [wintypes.DWORD, ctypes.POINTER(NOTIFYICONDATAW)]
shell32.Shell_NotifyIconW.restype = wintypes.BOOL


def log_line(message: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(message.rstrip() + "\n")
    except OSError:
        pass


def build_tray_tooltip(url: str) -> str:
    tooltip = f"{APP_NAME} - {url}"
    return tooltip[:127]


def make_int_resource(resource_id: int) -> wintypes.LPCWSTR:
    return ctypes.cast(ctypes.c_void_p(resource_id), wintypes.LPCWSTR)


class WebUiTrayApp:
    def __init__(self, server: object, url: str, *, open_browser_on_start: bool) -> None:
        self.server = server
        self.url = url
        self.open_browser_on_start = open_browser_on_start
        self.tooltip = build_tray_tooltip(url)
        self.hinstance = kernel32.GetModuleHandleW(None)
        self.class_name = f"CodexSessionToolkitTrayWindow-{kernel32.GetCurrentProcessId()}"
        self.window_proc = WNDPROC(self._window_proc)
        self.class_atom = 0
        self.hwnd: int | None = None
        self.icon_handle: int | None = None
        self.is_closing = False
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            name="codex-session-toolkit-webui",
            daemon=True,
        )

    def run(self) -> int:
        log_line("tray_app.run:start")
        self.server_thread.start()
        log_line("tray_app.run:server_thread_started")
        if self.open_browser_on_start:
            threading.Timer(0.4, self.open_web_ui).start()
            log_line("tray_app.run:browser_timer_started")
        self._create_window()
        log_line("tray_app.run:window_created")
        self._add_tray_icon()
        log_line("tray_app.run:tray_icon_added")
        try:
            log_line("tray_app.run:message_loop_enter")
            self._message_loop()
        finally:
            log_line("tray_app.run:cleanup")
            self._cleanup()
        return 0

    def open_web_ui(self) -> None:
        log_line(f"tray_app.open_web_ui:{self.url}")
        try:
            os.startfile(self.url)  # type: ignore[attr-defined]
            log_line("tray_app.open_web_ui:startfile_ok")
            return
        except Exception as exc:  # noqa: BLE001
            log_line(f"tray_app.open_web_ui:startfile_failed:{exc}")
        webbrowser.open(self.url)

    def request_exit(self) -> None:
        if self.hwnd:
            user32.PostMessageW(self.hwnd, WM_COMMAND, EXIT_COMMAND, 0)
            return
        self._close_from_window_thread()

    def _close_from_window_thread(self) -> None:
        if self.is_closing:
            return
        self.is_closing = True
        try:
            self.server.shutdown()
        except Exception:
            pass
        if self.hwnd:
            user32.DestroyWindow(self.hwnd)

    def _create_window(self) -> None:
        wnd_class = WNDCLASSW()
        wnd_class.lpfnWndProc = self.window_proc
        wnd_class.hInstance = self.hinstance
        wnd_class.lpszClassName = self.class_name
        self.class_atom = user32.RegisterClassW(ctypes.byref(wnd_class))
        if not self.class_atom:
            raise RuntimeError("Failed to register the tray window class.")

        hwnd = user32.CreateWindowExW(
            0,
            self.class_name,
            APP_NAME,
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            self.hinstance,
            None,
        )
        if not hwnd:
            raise RuntimeError("Failed to create the tray window.")
        self.hwnd = hwnd
        log_line(f"tray_app._create_window:hwnd={hwnd}")

    def _load_icon_handle(self) -> int:
        icon_handle = user32.LoadIconW(None, make_int_resource(IDI_APPLICATION))
        if not icon_handle:
            raise RuntimeError("Failed to load the tray icon.")
        return icon_handle

    def _add_tray_icon(self) -> None:
        if self.hwnd is None:
            raise RuntimeError("Tray window is not ready.")
        self.icon_handle = self._load_icon_handle()
        notify_data = NOTIFYICONDATAW()
        notify_data.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        notify_data.hWnd = self.hwnd
        notify_data.uID = TRAY_ICON_UID
        notify_data.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
        notify_data.uCallbackMessage = TRAY_CALLBACK_MESSAGE
        notify_data.hIcon = self.icon_handle
        notify_data.szTip = self.tooltip
        if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(notify_data)):
            raise RuntimeError("Failed to add the tray icon.")
        log_line("tray_app._add_tray_icon:ok")

    def _remove_tray_icon(self) -> None:
        if self.hwnd is None:
            return
        notify_data = NOTIFYICONDATAW()
        notify_data.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
        notify_data.hWnd = self.hwnd
        notify_data.uID = TRAY_ICON_UID
        shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(notify_data))

    def _show_context_menu(self) -> None:
        if self.hwnd is None:
            return
        menu = user32.CreatePopupMenu()
        if not menu:
            return
        try:
            user32.AppendMenuW(menu, MF_STRING, OPEN_WEB_UI_COMMAND, "Open Web UI")
            user32.AppendMenuW(menu, MF_SEPARATOR, 0, None)
            user32.AppendMenuW(menu, MF_STRING, EXIT_COMMAND, "Exit")
            cursor = POINT()
            user32.GetCursorPos(ctypes.byref(cursor))
            user32.SetForegroundWindow(self.hwnd)
            command = user32.TrackPopupMenu(
                menu,
                TPM_LEFTALIGN | TPM_BOTTOMALIGN | TPM_RIGHTBUTTON | TPM_RETURNCMD,
                cursor.x,
                cursor.y,
                0,
                self.hwnd,
                None,
            )
            if command == OPEN_WEB_UI_COMMAND:
                log_line("tray_app._show_context_menu:open")
                self.open_web_ui()
            elif command == EXIT_COMMAND:
                log_line("tray_app._show_context_menu:exit")
                self._close_from_window_thread()
            user32.PostMessageW(self.hwnd, WM_NULL, 0, 0)
        finally:
            user32.DestroyMenu(menu)

    def _message_loop(self) -> None:
        message = MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))

    def _cleanup(self) -> None:
        try:
            self.server.shutdown()
        except Exception:
            pass
        try:
            self.server.server_close()
        except Exception:
            pass
        if self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        try:
            self._remove_tray_icon()
        except Exception:
            pass
        if self.icon_handle:
            user32.DestroyIcon(self.icon_handle)
            self.icon_handle = None
        if self.class_atom:
            user32.UnregisterClassW(self.class_name, self.hinstance)
            self.class_atom = 0

    def _window_proc(
        self,
        hwnd: wintypes.HWND,
        message: int,
        wparam: wintypes.WPARAM,
        lparam: wintypes.LPARAM,
    ) -> int:
        if message == TRAY_CALLBACK_MESSAGE:
            event_code = int(lparam)
            if event_code in {WM_LBUTTONUP, WM_LBUTTONDBLCLK}:
                self.open_web_ui()
                return 0
            if event_code in {WM_RBUTTONUP, WM_CONTEXTMENU}:
                self._show_context_menu()
                return 0

        if message == WM_COMMAND:
            command = int(wparam) & 0xFFFF
            if command == OPEN_WEB_UI_COMMAND:
                self.open_web_ui()
                return 0
            if command == EXIT_COMMAND:
                self._close_from_window_thread()
                return 0

        if message == WM_DESTROY:
            self._remove_tray_icon()
            user32.PostQuitMessage(0)
            return 0

        return user32.DefWindowProcW(hwnd, message, wparam, lparam)


def run_webui_tray_app(
    *,
    codex_home: Path,
    initial_workdir: Path | None,
    accounts_root: Path | None,
    host: str,
    port: int,
    open_browser: bool,
) -> int:
    log_line("tray_app.run_webui_tray_app:create_server")
    server, url = create_webui_server(
        codex_home=codex_home,
        initial_workdir=initial_workdir,
        accounts_root=accounts_root,
        host=host,
        port=port,
    )
    log_line(f"tray_app.run_webui_tray_app:url={url}")
    app = WebUiTrayApp(server, url, open_browser_on_start=open_browser)
    return app.run()
