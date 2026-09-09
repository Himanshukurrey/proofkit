"""Best-effort, actionable hints for command-launch failures.

Written and reasoned through from code review and documented Python/Windows
behavior (see PLAN.md / README Limitations) — NOT verified on a real Windows
machine, since none was available while building this. Treat this as a
considered guess at the most common failure mode, not a confirmed fix.
"""
import platform
import shutil
from typing import List, Optional

# Extensions that require a command interpreter (cmd.exe) to run and can't be
# launched directly via subprocess's shell=False on Windows — this is the
# well-documented cause of "WinError 2: file not found" for tools like npm,
# yarn, and pnpm, which ship as .cmd wrappers on Windows (as does almost any
# Node-based CLI installed via npm, e.g. tsc/eslint/jest in node_modules/.bin).
_SHELL_REQUIRED_EXTENSIONS = (".cmd", ".bat", ".ps1")


def launch_error_hint(argv: List[str]) -> Optional[str]:
    """If launching `argv` failed and it looks like the Windows .cmd/.bat shim
    issue, return an actionable hint. Returns None otherwise (including on
    non-Windows platforms, where this doesn't apply)."""
    if platform.system() != "Windows" or not argv:
        return None

    resolved = shutil.which(argv[0])
    if not resolved or not resolved.lower().endswith(_SHELL_REQUIRED_EXTENSIONS):
        return None

    quoted_cmd = " ".join(argv)
    return (
        f"'{argv[0]}' exists but is a {resolved.rsplit('.', 1)[-1]} script "
        "(common for npm/yarn/pnpm and other Node-based tools on Windows) — "
        "these need a command interpreter to run, which proofkit deliberately "
        "doesn't invoke on your behalf (see README: no shell=True, so quoting "
        "behaves the same on every machine). Workaround: run it through cmd "
        f"explicitly — `proofkit capture -- cmd /c {quoted_cmd}`."
    )
