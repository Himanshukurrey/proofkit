"""Collect basic, non-sensitive platform information for a manifest."""
import platform
import sys
from typing import TypedDict


class PlatformInfo(TypedDict):
    system: str
    release: str
    machine: str
    python_version: str


def collect_platform_info() -> PlatformInfo:
    """Return OS/arch/interpreter info. No paths, no usernames, no env values."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python_version": "{}.{}.{}".format(*sys.version_info[:3]),
    }
