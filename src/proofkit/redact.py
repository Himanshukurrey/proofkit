"""Name-pattern based redaction for captured environment variables.

Explicitly NOT a full secrets scanner: this only looks at variable
*names*, not values. A variable named `MY_APP_CONFIG` holding a raw API
key would slip through. Document this limitation loudly in the README —
don't let users believe this is safe to point at anything sensitive
without reviewing the artifact themselves first.
"""

import re

# Case-insensitive substrings that mark a variable name as likely-sensitive.
SECRET_KEY_PATTERNS = [
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "CREDENTIAL",
    "AUTH",
    "ACCESS_KEY",
    "PRIVATE",
]

REDACTED_VALUE = "<redacted>"

_pattern_re = re.compile("|".join(re.escape(p) for p in SECRET_KEY_PATTERNS), re.IGNORECASE)


def redact_env(env: dict[str, str]) -> tuple[dict[str, str], list]:
    """Return (safe_env, redacted_keys) — values whose *name* looks sensitive are replaced."""
    safe_env: dict[str, str] = {}
    redacted_keys = []
    for key, value in env.items():
        if _pattern_re.search(key):
            safe_env[key] = REDACTED_VALUE
            redacted_keys.append(key)
        else:
            safe_env[key] = value
    return safe_env, redacted_keys
