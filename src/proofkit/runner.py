"""Run a command and capture its outcome.

Always shell=False: proofkit never interprets shell syntax itself, so
there's no shell-quoting inconsistency across machines/default shells.
If a user needs `&&`/pipes, they wrap it themselves:
`proofkit capture -- bash -c "cmd1 && cmd2"`.
"""

import subprocess
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionResult:
    argv: list[str]
    exit_code: Optional[int]
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool
    launch_error: Optional[str]


def run_command(argv: list[str], cwd: str, timeout: int) -> ExecutionResult:
    """Run `argv` in `cwd`, capturing stdout/stderr/exit code. Never raises for a normal failure."""
    start = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.monotonic() - start
        return ExecutionResult(
            argv=argv,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            duration_seconds=duration,
            timed_out=False,
            launch_error=None,
        )
    except subprocess.TimeoutExpired as e:
        duration = time.monotonic() - start
        return ExecutionResult(
            argv=argv,
            exit_code=None,
            stdout=(e.stdout or ""),
            stderr=(e.stderr or ""),
            duration_seconds=duration,
            timed_out=True,
            launch_error=None,
        )
    except OSError as e:
        # e.g. command not found, permission denied
        duration = time.monotonic() - start
        return ExecutionResult(
            argv=argv,
            exit_code=None,
            stdout="",
            stderr="",
            duration_seconds=duration,
            timed_out=False,
            launch_error=str(e),
        )
