"""Tests for the Windows .cmd/.bat launch-failure hint.

These mock platform.system()/shutil.which() to exercise the logic
deterministically — they verify the code does what it's supposed to do,
NOT that the underlying Windows behavior being modeled is correct. No
Windows machine was available while building this; see README Limitations.
"""

from unittest.mock import patch

from proofkit.diagnostics import launch_error_hint


def test_returns_none_on_non_windows():
    with patch("proofkit.diagnostics.platform.system", return_value="Darwin"):
        assert launch_error_hint(["npm", "test"]) is None


def test_returns_none_on_windows_when_command_not_found_at_all():
    with (
        patch("proofkit.diagnostics.platform.system", return_value="Windows"),
        patch("proofkit.diagnostics.shutil.which", return_value=None),
    ):
        assert launch_error_hint(["totally-made-up-binary"]) is None


def test_returns_none_on_windows_for_a_real_exe():
    with (
        patch("proofkit.diagnostics.platform.system", return_value="Windows"),
        patch("proofkit.diagnostics.shutil.which", return_value=r"C:\Python311\python.exe"),
    ):
        assert launch_error_hint(["python", "script.py"]) is None


def test_returns_hint_on_windows_for_a_cmd_shim():
    with (
        patch("proofkit.diagnostics.platform.system", return_value="Windows"),
        patch(
            "proofkit.diagnostics.shutil.which",
            return_value=r"C:\Program Files\nodejs\npm.cmd",
        ),
    ):
        hint = launch_error_hint(["npm", "test"])
        assert hint is not None
        assert "cmd" in hint.lower()
        assert "proofkit capture -- cmd /c npm test" in hint


def test_returns_hint_for_bat_shim_too():
    with (
        patch("proofkit.diagnostics.platform.system", return_value="Windows"),
        patch("proofkit.diagnostics.shutil.which", return_value=r"C:\tools\yarn.bat"),
    ):
        assert launch_error_hint(["yarn", "install"]) is not None


def test_empty_argv_returns_none():
    with patch("proofkit.diagnostics.platform.system", return_value="Windows"):
        assert launch_error_hint([]) is None
