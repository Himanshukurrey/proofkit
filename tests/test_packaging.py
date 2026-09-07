from proofkit.packaging import read_proof_archive, write_proof_archive


def test_write_then_read_round_trip(tmp_path):
    manifest = {
        "proofkit_version": "0.1.0",
        "capture_id": "test-id",
        "command": {"argv": ["python", "script.py"]},
        "execution": {"exit_code": 1, "duration_seconds": 0.1, "timed_out": False, "launch_error": None},
        "output": {
            "stdout_path": "stdout.txt",
            "stderr_path": "stderr.txt",
            "stdout_sha256": "irrelevant-for-this-test",
            "stderr_sha256": "irrelevant-for-this-test",
            "stdout_bytes": 0,
            "stderr_bytes": 5,
            "truncated": False,
            "stderr_signature": "Error: boom",
        },
        "environment": {"platform": {}, "env_captured": False, "env_vars": {}, "redacted_keys": []},
        "git": {"is_repo": False, "commit_hash": None, "branch": None, "is_dirty": None},
    }

    archive_path = str(tmp_path / "bug.proof")
    write_proof_archive(archive_path, manifest, stdout="hello", stderr="Error: boom")

    read_manifest, stdout, stderr = read_proof_archive(archive_path)

    assert read_manifest == manifest
    assert stdout == "hello"
    assert stderr == "Error: boom"


def test_archive_is_a_plain_inspectable_zip(tmp_path):
    import zipfile

    manifest = {
        "output": {"stdout_path": "stdout.txt", "stderr_path": "stderr.txt"},
    }
    archive_path = str(tmp_path / "bug.proof")
    write_proof_archive(archive_path, manifest, stdout="", stderr="")

    assert zipfile.is_zipfile(archive_path)
    with zipfile.ZipFile(archive_path) as zf:
        names = set(zf.namelist())
        assert names == {"manifest.json", "stdout.txt", "stderr.txt"}
