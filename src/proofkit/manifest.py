"""Build and serialize the proof manifest — the JSON record inside a .proof archive."""
import hashlib
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


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def extract_stderr_signature(stderr: str) -> Optional[str]:
    """Return the last non-empty line of stderr — reliably the `SomeError: message`
    line of a traceback in Python/Node/Go/etc. Used by `verify` to check whether
    the same failure is still present after a replay."""
    for line in reversed(stderr.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
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
