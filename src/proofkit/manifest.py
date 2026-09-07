"""Build and serialize the proof manifest — the JSON record inside a .proof archive."""
import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from proofkit import __version__
from proofkit.gitinfo import GitInfo
from proofkit.platforminfo import PlatformInfo
from proofkit.runner import ExecutionResult

# Truncate captured output past this size so a runaway command can't produce
# an unusably large artifact. Full functional streaming/tee'ing is out of
# scope for v1 — see PLAN.md.
MAX_CAPTURED_BYTES = 10 * 1024 * 1024  # 10MB

# Known runtime "footer" lines that follow the real error line and would
# otherwise be mistaken for the signature. Discovered by actually running
# the Node.js demo: Node prints "Node.js vX.Y.Z" as the last line after an
# uncaught exception's stack trace. Add more here as other runtimes'
# quirks are found — this is a known, incomplete list, not a general
# solution (see PLAN.md's limitations on cross-language support).
_IGNORED_TRAILING_PATTERNS = [
    re.compile(r"^Node\.js v\d+\.\d+\.\d+$"),
]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def extract_stderr_signature(stderr: str) -> Optional[str]:
    """Return the `SomeError: message` line of a traceback, scanning from the
    end of stderr. Handles two different conventions:

    - Python: the error line IS the last line (e.g. `IndexError: ...`).
    - Node/JS (and others): the error line is followed by indented `at ...`
      stack-frame lines and a trailing runtime footer.

    So: skip empty lines, skip known footer lines, skip lines that are
    indented (stack-frame continuations in both conventions are indented;
    the actual error line is not) — return the first line left standing.
    This is a heuristic tuned against Python and Node's actual output
    (verified manually against both demos), not a general parser for every
    language's error format."""
    for line in reversed(stderr.splitlines()):
        if not line.strip():
            continue
        if line[0].isspace():
            continue  # indented stack-frame line, not the error message itself
        if any(pattern.match(line.strip()) for pattern in _IGNORED_TRAILING_PATTERNS):
            continue
        return line.strip()
    return None


def _truncate(text: str) -> tuple:
    data = text.encode("utf-8", errors="replace")
    if len(data) <= MAX_CAPTURED_BYTES:
        return text, False
    truncated = data[:MAX_CAPTURED_BYTES].decode("utf-8", errors="ignore")
    return truncated, True


def build_manifest(
    execution: ExecutionResult,
    platform_info: PlatformInfo,
    git_info: GitInfo,
    env_captured: bool,
    env_vars: Dict[str, str],
    redacted_keys: List[str],
    note: Optional[str] = None,
) -> tuple:
    """Assemble the manifest dict matching the schema documented in PLAN.md.

    Returns (manifest, stdout, stderr) — the stdout/stderr are the
    *truncated* versions that the manifest's hashes/sizes describe, so
    callers writing a .proof archive store exactly what was hashed.
    """
    stdout, stdout_truncated = _truncate(execution.stdout)
    stderr, stderr_truncated = _truncate(execution.stderr)

    manifest: Dict[str, Any] = {
        "proofkit_version": __version__,
        "capture_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command": {"argv": execution.argv},
        "execution": {
            "exit_code": execution.exit_code,
            "duration_seconds": round(execution.duration_seconds, 3),
            "timed_out": execution.timed_out,
            "launch_error": execution.launch_error,
        },
        "output": {
            "stdout_path": "stdout.txt",
            "stderr_path": "stderr.txt",
            "stdout_sha256": _sha256(stdout),
            "stderr_sha256": _sha256(stderr),
            "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
            "stderr_bytes": len(stderr.encode("utf-8", errors="replace")),
            "truncated": stdout_truncated or stderr_truncated,
            "stderr_signature": extract_stderr_signature(execution.stderr),
        },
        "environment": {
            "platform": platform_info,
            "env_captured": env_captured,
            "env_vars": env_vars,
            "redacted_keys": redacted_keys,
        },
        "git": dict(git_info),
    }
    if note:
        manifest["note"] = note
    return manifest, stdout, stderr
