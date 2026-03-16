import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from webui.server import build_browser_url  # noqa: E402
from webui.tray_app import APP_NAME, build_tray_tooltip  # noqa: E402


class WebUiServerHelperTests(unittest.TestCase):
    def test_build_browser_url_normalizes_wildcard_hosts(self) -> None:
        self.assertEqual(build_browser_url("0.0.0.0", 8765), "http://127.0.0.1:8765")
        self.assertEqual(build_browser_url("::", 9000), "http://127.0.0.1:9000")
        self.assertEqual(build_browser_url("::1", 8765), "http://[::1]:8765")

    def test_build_tray_tooltip_keeps_app_name_and_fits_notify_icon_limit(self) -> None:
        tooltip = build_tray_tooltip("http://127.0.0.1:8765/" + ("x" * 300))
        self.assertTrue(tooltip.startswith(APP_NAME))
        self.assertLessEqual(len(tooltip), 127)


if __name__ == "__main__":
    unittest.main()
