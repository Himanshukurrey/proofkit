"""End-to-end test driving the real CLI (via Click's CliRunner) against the
actual demo bug — exercises the full capture -> verify loop with a real
subprocess execution underneath, not mocks."""

import os
import sys
from pathlib import Path

from click.testing import CliRunner

from proofkit.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_SCRIPT = REPO_ROOT / "demo" / "top_n_buggy.py"


def _capture_the_demo_bug(tmp_path):
    runner = CliRunner()
    proof_path = str(tmp_path / "bug.proof")
    result = runner.invoke(
        main,
        [
            "capture",
            "-o",
            proof_path,
            "--",
            sys.executable,
            str(DEMO_SCRIPT),
            "5",
            "3",
            "9",
            "1",
            "7",
            "5",
        ],
    )
    assert result.exit_code == 0, result.output
    assert os.path.exists(proof_path)
    return proof_path


def test_capture_then_verify_still_failing(tmp_path):
    proof_path = _capture_the_demo_bug(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["verify", proof_path, "--allow-same-commit"])

    assert "STILL FAILING" in result.output
    assert result.exit_code == 1


def test_verify_without_allow_same_commit_warns_and_exits_2(tmp_path):
    proof_path = _capture_the_demo_bug(tmp_path)

    runner = CliRunner()
    result = runner.invoke(main, ["verify", proof_path])

    assert result.exit_code == 2
    assert "same git commit" in result.output


def test_capture_records_correct_signature(tmp_path):
    proof_path = _capture_the_demo_bug(tmp_path)

    from proofkit.packaging import read_proof_archive

    manifest, _stdout, _stderr = read_proof_archive(proof_path)
    assert manifest["execution"]["exit_code"] == 1
    assert manifest["output"]["stderr_signature"] == "IndexError: list index out of range"


def test_capture_records_cwd(tmp_path, monkeypatch):
    capture_dir = tmp_path / "capture_here"
    capture_dir.mkdir()
    monkeypatch.chdir(capture_dir)

    proof_path = _capture_the_demo_bug(tmp_path)

    from proofkit.packaging import read_proof_archive

    manifest, _stdout, _stderr = read_proof_archive(proof_path)
    assert manifest["command"]["cwd"] == str(capture_dir.resolve())


def test_verify_from_different_directory_warns_about_cwd_drift(tmp_path, monkeypatch):
    # Real-world scenario reported by a reviewer: capture in one directory,
    # verify from another without --cwd. The relative path in argv then
    # resolves against the wrong (or missing) file, which can make the
    # heuristic verdict misleadingly say FIXED — the command "changed" only
    # because it failed to even find the right file, not because the bug
    # is gone. This confirms the warning actually fires in that case.
    capture_dir = tmp_path / "capture_here"
    capture_dir.mkdir()
    replay_dir = tmp_path / "replay_elsewhere"
    replay_dir.mkdir()

    monkeypatch.chdir(capture_dir)
    proof_path = _capture_the_demo_bug(tmp_path)

    monkeypatch.chdir(replay_dir)
    runner = CliRunner()
    result = runner.invoke(main, ["verify", proof_path])

    assert "replaying from" in result.output
    assert str(capture_dir.resolve()) in result.output
    assert "misleadingly report FIXED" in result.output


def test_verify_with_explicit_matching_cwd_does_not_warn(tmp_path, monkeypatch):
    capture_dir = tmp_path / "capture_here"
    capture_dir.mkdir()

    monkeypatch.chdir(capture_dir)
    proof_path = _capture_the_demo_bug(tmp_path)

    monkeypatch.chdir(tmp_path)  # verify invoked from elsewhere, but with --cwd pointing back
    runner = CliRunner()
    result = runner.invoke(main, ["verify", proof_path, "--cwd", str(capture_dir), "--allow-same-commit"])

    assert "replaying from" not in result.output
