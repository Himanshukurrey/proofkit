"""Compare a captured failure against a replayed run and produce a verdict.

This is a heuristic, not a full functional check — documented loudly in
the README. It answers "is the same crash still happening", not "is the
feature correct". An agent that hides a bug behind a try/except instead
of fixing it will make this report FIXED. Pair with a real test suite.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from proofkit.manifest import extract_stderr_signature


class Verdict(str, Enum):
    STILL_FAILING = "STILL FAILING"
    FIXED = "FIXED"
    CHANGED = "CHANGED"  # different error/exit code combination — needs manual review


@dataclass
class ComparisonResult:
    verdict: Verdict
    captured_exit_code: Optional[int]
    replayed_exit_code: Optional[int]
    captured_signature: Optional[str]
    replayed_signature: Optional[str]


def compare(
    captured_exit_code: Optional[int],
    captured_signature: Optional[str],
    replayed_exit_code: Optional[int],
    replayed_stderr: str,
) -> ComparisonResult:
    replayed_signature = extract_stderr_signature(replayed_stderr)

    exit_matches = captured_exit_code == replayed_exit_code
    signature_still_present = bool(captured_signature) and captured_signature == replayed_signature

    if exit_matches and signature_still_present:
        verdict = Verdict.STILL_FAILING
    elif not exit_matches and not signature_still_present:
        verdict = Verdict.FIXED
    else:
        # e.g. same exit code but a different error, or exit code changed
        # while the same signature somehow persists — ambiguous, don't guess
        verdict = Verdict.CHANGED

    return ComparisonResult(
        verdict=verdict,
        captured_exit_code=captured_exit_code,
        replayed_exit_code=replayed_exit_code,
        captured_signature=captured_signature,
        replayed_signature=replayed_signature,
    )
