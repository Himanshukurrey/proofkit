"""Pack/unpack a .proof artifact — a plain zip containing manifest.json plus
the captured stdout/stderr. Deliberately just a zip: `unzip -l bug.proof`
works with no proofkit-specific tooling. Transparency over a custom format.
"""

import json
import zipfile
from typing import Any

MANIFEST_FILENAME = "manifest.json"


def write_proof_archive(path: str, manifest: dict[str, Any], stdout: str, stderr: str) -> None:
    """Write manifest + captured output into a zip at `path`."""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST_FILENAME, json.dumps(manifest, indent=2))
        zf.writestr(manifest["output"]["stdout_path"], stdout)
        zf.writestr(manifest["output"]["stderr_path"], stderr)


def read_proof_archive(path: str) -> tuple[dict[str, Any], str, str]:
    """Read a .proof archive, returning (manifest, stdout, stderr)."""
    with zipfile.ZipFile(path, mode="r") as zf:
        manifest = json.loads(zf.read(MANIFEST_FILENAME).decode("utf-8"))
        stdout = zf.read(manifest["output"]["stdout_path"]).decode("utf-8", errors="replace")
        stderr = zf.read(manifest["output"]["stderr_path"]).decode("utf-8", errors="replace")
    return manifest, stdout, stderr
