"""Implementation of `proofkit verify`.

Replays the exact command captured in a .proof archive and reports
whether the original failure still reproduces. The same-commit check
before replaying is the guardrail that makes the "did the agent's fix
actually work" use case trustworthy rather than theater: without it,
running verify against completely unchanged code could still print a
verdict, silently making "nothing happened" look meaningful.
"""
import os
import sys

import click

from proofkit.compare import Verdict, compare
from proofkit.gitinfo import collect_git_info
from proofkit.packaging import read_proof_archive
from proofkit.runner import run_command

_VERDICT_COLOR = {
    Verdict.STILL_FAILING: "red",
    Verdict.FIXED: "green",
    Verdict.CHANGED: "yellow",
}


def run_verify(proof_path: str, cwd: str, allow_same_commit: bool) -> None:
    manifest, _captured_stdout, captured_stderr = read_proof_archive(proof_path)

    replay_cwd = cwd or os.getcwd()
    argv = manifest["command"]["argv"]

    captured_git = manifest.get("git", {})
    if captured_git.get("is_repo"):
        current_git = collect_git_info(replay_cwd)
        if (
            current_git["is_repo"]
            and current_git["commit_hash"] == captured_git.get("commit_hash")
            and not allow_same_commit
        ):
            click.secho(
                "⚠ Warning: replaying against the exact same git commit that was "
                "captured — nothing has changed, so this verdict doesn't tell you "
                "whether a fix worked. Pass --allow-same-commit to proceed anyway.",
                fg="yellow",
            )
            sys.exit(2)

    click.echo(f"Replaying: {' '.join(argv)}")
    execution = run_command(argv, cwd=replay_cwd, timeout=120)

    if execution.launch_error:
        click.secho(f"Could not launch command: {execution.launch_error}", fg="red")
        sys.exit(1)

    result = compare(
        captured_exit_code=manifest["execution"]["exit_code"],
        captured_signature=manifest["output"]["stderr_signature"],
        replayed_exit_code=execution.exit_code,
        replayed_stderr=execution.stderr,
    )

    click.echo()
    click.echo(f"Captured exit code:  {result.captured_exit_code}")
    click.echo(f"Replayed exit code:  {result.replayed_exit_code}")
    click.echo(f"Captured signature:  {result.captured_signature or '(none)'}")
    click.echo(f"Replayed signature:  {result.replayed_signature or '(none)'}")
    click.echo()

    color = _VERDICT_COLOR[result.verdict]
    click.secho(result.verdict.value, fg=color, bold=True)

    if result.verdict == Verdict.CHANGED:
        click.secho(
            "The result doesn't cleanly match either the original failure or a "
            "clean fix — review the captured vs. replayed output above yourself.",
            fg="yellow",
        )

    sys.exit(0 if result.verdict == Verdict.FIXED else 1)
