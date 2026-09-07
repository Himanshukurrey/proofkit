"""ProofKit command-line interface.

Two commands:
  proofkit capture -- <command> [args...]   capture a failure as a portable .proof artifact
  proofkit verify <bug.proof>                replay the captured command and verdict on it
"""
import click

from proofkit import __version__


@click.group()
@click.version_option(version=__version__, prog_name="proofkit")
def main() -> None:
    """ProofKit — catch false "I fixed it" claims from AI coding agents.

    Capture a bug once, verify the fix anywhere.
    """


@main.command(context_settings={"ignore_unknown_options": True})
@click.option("-o", "--output", "output_path", default=None, help="Path to write the .proof artifact to.")
@click.option("--timeout", default=120, show_default=True, help="Max seconds to let the command run.")
@click.option("--with-env", is_flag=True, default=False, help="Capture environment variables (name-pattern redacted).")
@click.option("--note", default=None, help="Optional free-text note to store in the manifest.")
@click.argument("cmd", nargs=-1, type=click.UNPROCESSED, required=True)
def capture(output_path, timeout, with_env, note, cmd) -> None:
    """Run CMD and capture a portable proof of its failure (or success)."""
    from proofkit.capture_cmd import run_capture

    run_capture(list(cmd), output_path=output_path, timeout=timeout, with_env=with_env, note=note)


@main.command()
@click.argument("proof_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--cwd", "cwd", default=None, type=click.Path(exists=True, file_okay=False), help="Directory to replay the command in (default: current directory).")
@click.option("--allow-same-commit", is_flag=True, default=False, help="Skip the warning when replaying against the exact same git commit that was captured.")
def verify(proof_path, cwd, allow_same_commit) -> None:
    """Replay the command captured in PROOF_PATH and report whether the failure still reproduces."""
    from proofkit.verify_cmd import run_verify

    run_verify(proof_path, cwd=cwd, allow_same_commit=allow_same_commit)
