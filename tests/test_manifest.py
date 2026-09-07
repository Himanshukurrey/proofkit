from proofkit.gitinfo import collect_git_info
from proofkit.manifest import build_manifest, extract_stderr_signature
from proofkit.platforminfo import collect_platform_info
from proofkit.runner import ExecutionResult

PYTHON_STDERR = """Traceback (most recent call last):
  File "top_n_buggy.py", line 17, in <module>
    print(top_n(items, int(n_arg)))
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "top_n_buggy.py", line 11, in top_n
    return sorted_items[n]  # bug: should be sorted_items[:n]
           ~~~~~~~~~~~~^^^
IndexError: list index out of range
"""

NODE_STDERR = """/path/top_n_buggy.js:14
console.log(result.toFixed(2));
                   ^

TypeError: Cannot read properties of undefined (reading 'toFixed')
    at Object.<anonymous> (/path/top_n_buggy.js:14:20)
    at Module._compile (node:internal/modules/cjs/loader:1934:14)
    at node:internal/main/run_main_module:33:47

Node.js v26.8.1
"""


def test_extract_signature_from_python_traceback():
    assert extract_stderr_signature(PYTHON_STDERR) == "IndexError: list index out of range"


def test_extract_signature_from_node_traceback_skips_stack_frames_and_footer():
    assert (
        extract_stderr_signature(NODE_STDERR)
        == "TypeError: Cannot read properties of undefined (reading 'toFixed')"
    )


def test_extract_signature_from_empty_stderr_returns_none():
    assert extract_stderr_signature("") is None
    assert extract_stderr_signature("   \n  \n") is None


def test_build_manifest_smoke():
    execution = ExecutionResult(
        argv=["python", "demo/top_n_buggy.py", "5"],
        exit_code=1,
        stdout="",
        stderr=PYTHON_STDERR,
        duration_seconds=0.02,
        timed_out=False,
        launch_error=None,
    )
    manifest, stdout, stderr = build_manifest(
        execution=execution,
        platform_info=collect_platform_info(),
        git_info={"is_repo": False, "commit_hash": None, "branch": None, "is_dirty": None},
        env_captured=False,
        env_vars={},
        redacted_keys=[],
    )

    assert manifest["execution"]["exit_code"] == 1
    assert manifest["output"]["stderr_signature"] == "IndexError: list index out of range"
    assert manifest["environment"]["env_captured"] is False
    assert stdout == ""
    assert stderr == PYTHON_STDERR
    assert "proofkit_version" in manifest
    assert "capture_id" in manifest
