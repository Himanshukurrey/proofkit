from proofkit.compare import Verdict, compare


def test_still_failing_when_exit_code_and_signature_match():
    result = compare(
        captured_exit_code=1,
        captured_signature="IndexError: list index out of range",
        replayed_exit_code=1,
        replayed_stderr="Traceback (most recent call last):\nIndexError: list index out of range\n",
    )
    assert result.verdict == Verdict.STILL_FAILING


def test_fixed_when_exit_code_differs_and_signature_gone():
    result = compare(
        captured_exit_code=1,
        captured_signature="IndexError: list index out of range",
        replayed_exit_code=0,
        replayed_stderr="",
    )
    assert result.verdict == Verdict.FIXED


def test_changed_when_same_exit_code_but_different_error():
    result = compare(
        captured_exit_code=1,
        captured_signature="IndexError: list index out of range",
        replayed_exit_code=1,
        replayed_stderr="ZeroDivisionError: division by zero\n",
    )
    assert result.verdict == Verdict.CHANGED


def test_changed_when_exit_code_differs_but_signature_somehow_persists():
    # Contrived, but exercises the remaining branch of the truth table.
    result = compare(
        captured_exit_code=1,
        captured_signature="Warning: deprecated",
        replayed_exit_code=0,
        replayed_stderr="Warning: deprecated\n",
    )
    assert result.verdict == Verdict.CHANGED


def test_handles_no_captured_signature():
    # A capture with no error (e.g. capturing a successful baseline by
    # mistake) shouldn't crash comparison. There was nothing to "fix", so
    # this correctly falls into CHANGED (needs manual review) rather than
    # falsely claiming FIXED — capture is meant for capturing failures.
    result = compare(
        captured_exit_code=0,
        captured_signature=None,
        replayed_exit_code=0,
        replayed_stderr="",
    )
    assert result.verdict == Verdict.CHANGED
