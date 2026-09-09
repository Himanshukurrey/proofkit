"""Implementation of `proofkit capture`: run a command, build its manifest,
and package everything into a portable .proof archive."""
import os
import sys
from datetime import datetime
from typing import List, Optional

import click

from proofkit.diagnostics import launch_error_hint
from proofkit.gitinfo import collect_git_info
from proofkit.manifest import build_manifest
from proofkit.packaging import write_proof_archive
from proofkit.platforminfo import collect_platform_info
from proofkit.redact import redact_env
from proofkit.runner import run_command


def _default_output_path() -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"proof-{timestamp}.proof"


def run_capture(
    argv: List[str],
    output_path: Optional[str],
    timeout: int,
    with_env: bool,
    note: Optional[str],
) -> None:
    cwd = os.getcwd()

    click.echo(f"Running: {' '.join(argv)}")
    execution = run_command(argv, cwd=cwd, timeout=timeout)

    if execution.launch_error:
        click.secho(f"Could not launch command: {execution.launch_error}", fg="red")
        hint = launch_error_hint(argv)
        if hint:
            click.secho(hint, fg="yellow")
        sys.exit(1)
    if execution.timed_out:
        click.secho(f"Command timed out after {timeout}s", fg="yellow")

    platform_info = collect_platform_info()
    git_info = collect_git_info(cwd)

    env_vars = {}
    redacted_keys = []
    if with_env:
        safe_env, redacted_keys = redact_env(dict(os.environ))
        env_vars = safe_env

    manifest, stdout_for_archive, stderr_for_archive = build_manifest(
        execution=execution,
        platform_info=platform_info,
        git_info=git_info,
        env_captured=with_env,
        env_vars=env_vars,
        redacted_keys=redacted_keys,
        note=note,
    )

    final_output_path = output_path or _default_output_path()
    write_proof_archive(final_output_path, manifest, stdout_for_archive, stderr_for_archive)

    click.echo()
    click.echo(f"Exit code:  {execution.exit_code}")
    click.echo(f"Duration:   {execution.duration_seconds:.3f}s")
    if manifest["output"]["stderr_signature"]:
        click.echo(f"Signature:  {manifest['output']['stderr_signature']}")
    if git_info["is_repo"]:
        dirty = " (dirty)" if git_info["is_dirty"] else ""
        click.echo(f"Git:        {git_info['commit_hash'][:12]}{dirty} on {git_info['branch']}")
    if redacted_keys:
        click.echo(f"Redacted:   {len(redacted_keys)} env var(s) by name pattern")

    click.echo()
    click.secho(f"Wrote {final_output_path}", fg="green")
