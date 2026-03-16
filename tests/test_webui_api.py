import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from webui.api import ToolkitWebService, coerce_existing_workdirs, merge_workdir_history  # noqa: E402


def create_accounts_root(root: Path, name: str) -> Path:
    account_root = root / name
    account_root.mkdir(parents=True, exist_ok=True)
    account_dir = account_root / "user1"
    account_dir.mkdir(parents=True, exist_ok=True)
    (account_dir / "config.toml").write_text('model_provider = "openai"\n', encoding="utf-8")
    (account_dir / "auth.json").write_text('{"auth_mode": "chatgpt"}\n', encoding="utf-8")
    return account_root


class WebUiApiTests(unittest.TestCase):
    def test_coerce_existing_workdirs_filters_missing_entries_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()

            result = coerce_existing_workdirs(
                [
                    "",
                    str(first),
                    str(root / "missing"),
                    str(second),
                    str(first),
                ],
                max_count=5,
            )

            self.assertEqual(result, [str(first.resolve()), str(second.resolve())])

    def test_merge_workdir_history_prioritizes_current_then_initial_then_saved(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            current = root / "current"
            initial = root / "initial"
            saved = root / "saved"
            current.mkdir()
            initial.mkdir()
            saved.mkdir()

            result = merge_workdir_history(
                str(current),
                {
                    "last_workdir": str(saved),
                    "recent_workdirs": [str(initial), str(current)],
                    "accounts_root_override": "",
                },
                initial_workdir=initial,
                max_count=5,
            )

            self.assertEqual(
                result,
                [
                    str(current.resolve()),
                    str(initial.resolve()),
                    str(saved.resolve()),
                ],
            )

    def test_accounts_root_update_persists_for_new_service_instances(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workdir = root / "workspace"
            workdir.mkdir()
            state_path = root / "workspace-state.json"
            first_accounts_root = create_accounts_root(root, "accounts-a")
            second_accounts_root = create_accounts_root(root, "accounts-b")

            service = ToolkitWebService(
                codex_home=root / ".codex",
                accounts_root=first_accounts_root,
                initial_workdir=workdir,
                workspace_state_path=state_path,
                legacy_workspace_state_path=root / "legacy-workspace-state.json",
            )
            bootstrap = service.get_bootstrap(str(workdir))
            self.assertEqual(bootstrap["configuredAccountsRoot"], str(first_accounts_root.resolve()))

            updated = service.update_accounts_root(str(second_accounts_root), requested_workdir=str(workdir))
            self.assertEqual(updated["configuredAccountsRoot"], str(second_accounts_root.resolve()))
            self.assertEqual(updated["accountsRoot"], str(second_accounts_root.resolve()))

            restored = ToolkitWebService(
                codex_home=root / ".codex",
                initial_workdir=workdir,
                workspace_state_path=state_path,
                legacy_workspace_state_path=root / "legacy-workspace-state.json",
            )
            restored_bootstrap = restored.get_bootstrap(str(workdir))
            self.assertEqual(
                restored_bootstrap["configuredAccountsRoot"],
                str(second_accounts_root.resolve()),
            )
            self.assertEqual(restored_bootstrap["accountsRoot"], str(second_accounts_root.resolve()))


if __name__ == "__main__":
    unittest.main()
