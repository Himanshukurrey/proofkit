from proofkit.redact import REDACTED_VALUE, redact_env


def test_redacts_names_matching_secret_patterns():
    env = {
        "MY_API_KEY": "abc123",
        "DB_PASSWORD": "hunter2",
        "AUTH_TOKEN": "xyz",
        "SAFE_VAR": "hello",
        "HOME": "/home/user",
    }
    safe_env, redacted_keys = redact_env(env)

    assert safe_env["MY_API_KEY"] == REDACTED_VALUE
    assert safe_env["DB_PASSWORD"] == REDACTED_VALUE
    assert safe_env["AUTH_TOKEN"] == REDACTED_VALUE
    assert safe_env["SAFE_VAR"] == "hello"
    assert safe_env["HOME"] == "/home/user"

    assert set(redacted_keys) == {"MY_API_KEY", "DB_PASSWORD", "AUTH_TOKEN"}


def test_matching_is_case_insensitive():
    safe_env, redacted_keys = redact_env({"my_secret_value": "shh"})
    assert safe_env["my_secret_value"] == REDACTED_VALUE
    assert redacted_keys == ["my_secret_value"]


def test_empty_env_returns_empty():
    safe_env, redacted_keys = redact_env({})
    assert safe_env == {}
    assert redacted_keys == []


def test_no_matches_leaves_everything_untouched():
    env = {"LANG": "en_US.UTF-8", "SHELL": "/bin/zsh", "PATH": "/usr/bin"}
    safe_env, redacted_keys = redact_env(env)
    assert safe_env == env
    assert redacted_keys == []
