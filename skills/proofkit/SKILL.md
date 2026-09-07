---
name: proofkit
description: Verify that a bug fix actually works instead of assuming it from a passing command. Use this before starting work on a reported bug or crash (to capture it), and again right after applying a fix (to verify it), whenever the user reports a bug, asks you to fix a crash/failing command, or asks you to confirm a fix actually works.
allowed-tools: Bash(proofkit *)
---

# ProofKit: verify fixes instead of assuming them

An exit code of 0 or a passing test doesn't prove a bug is fixed — it's possible
to satisfy either without truly fixing anything (for example, catching and
swallowing the original error). ProofKit closes that gap: capture the exact
failing command once, and get an objective, independent verdict later on
whether it's actually fixed.

Check `proofkit` is installed before using this skill: `proofkit --version`.
If it isn't, tell the user (`pip install git+https://github.com/Himanshukurrey/proofkit`)
and proceed without it rather than blocking on it.

## Workflow

**1. Before starting work on a reported bug**, capture it:

```
proofkit capture -o .proofkit/<short-slug>.proof -- <the exact failing command>
```

Use the precise command the user described (or one you've confirmed reproduces
the issue) — e.g. `pytest tests/test_foo.py`, `python script.py --flag`,
`npm test`. Works for any language; it just runs whatever command you give it.

Create the `.proofkit/` directory if it doesn't exist. Don't commit `.proof`
files to the repo — treat them as scratch artifacts for this session (suggest
adding `.proofkit/` to `.gitignore` if the project doesn't already ignore it).

**2. Make your fix as normal.**

**3. Before telling the user the bug is fixed, verify it:**

```
proofkit verify .proofkit/<short-slug>.proof
```

Important: `verify`'s guardrail compares the current git commit against the
one recorded at capture time, and refuses to give a verdict if they match —
because that would mean nothing has actually changed. If you've made the fix
but haven't committed it yet, either commit it first (cleanest), or pass
`--allow-same-commit` if you deliberately want to verify against an
uncommitted change (the guardrail only checks the commit hash, not working-
tree content, so it can't tell an uncommitted fix from no fix at all on its
own).

**4. Report the verdict honestly — don't override it with your own assumption:**

- **FIXED** — safe to tell the user the bug is resolved.
- **STILL FAILING** — the fix didn't work. Keep working; do not claim success.
- **CHANGED** — the failure is different now (different error, or an
  ambiguous exit-code/signature combination). Look at the captured-vs-replayed
  output ProofKit prints and figure out whether that's progress, a new bug, or
  a sign your fix didn't address the real cause — don't guess.

## Limitations to keep in mind

This is a heuristic (exit code + error-message match), not a full functional
check. It confirms the *specific captured crash* is gone, not that the
feature is correct — a fix that hides the bug behind a broad `try/except`
would still read as FIXED. Use this alongside the project's real test suite,
not instead of it.
