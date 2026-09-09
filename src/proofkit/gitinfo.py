"""Collect git repository context (commit, branch, dirty state) for a manifest.

Deliberately shallow: a commit hash + dirty flag is enough for verify's
same-commit guardrail. No diff content is captured in v1.
"""

import subprocess
from typing import Optional, TypedDict


class GitInfo(TypedDict):
    is_repo: bool
    commit_hash: Optional[str]
    branch: Optional[str]
    is_dirty: Optional[bool]


def _run_git(args: list, cwd: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def collect_git_info(cwd: str) -> GitInfo:
    """Return git context for `cwd`, or is_repo=False if it isn't inside a repo."""
    inside = _run_git(["rev-parse", "--is-inside-work-tree"], cwd)
    if inside != "true":
        return {"is_repo": False, "commit_hash": None, "branch": None, "is_dirty": None}

    commit_hash = _run_git(["rev-parse", "HEAD"], cwd)
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    status = _run_git(["status", "--porcelain"], cwd)

    return {
        "is_repo": True,
        "commit_hash": commit_hash,
        "branch": branch,
        "is_dirty": bool(status) if status is not None else None,
    }
