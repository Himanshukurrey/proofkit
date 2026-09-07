# ProofKit — Build Plan & Timeline to First GitHub Push

## Context

Across this session we exhaustively checked ~30+ "novel open-source project" ideas against live GitHub/web data, and every single one already existed except one gap: a tool that lets someone **capture a bug once and verify — objectively, not by trusting a claim — whether it's actually fixed later**, positioned specifically to catch AI coding agents (Claude Code, Cursor, etc.) asserting "fixed it" when they haven't. The closest prior art, `reprozip`, solved the technical core over a decade ago but stayed niche (362⭐) because it was framed as generic "reproducible research" tooling, not as an agent-honesty check — a framing that didn't exist until now.

The user (Python-proficient, all existing repos are Python; only Python 3.9.6 is installed locally, no Node/Rust) wants to build this as a real open-source project with a realistic shot at traction, and asked specifically: what's required, and how fast can a first version get posted to GitHub. They've confirmed: **build in Python** (fastest given their setup and skills), **language-agnostic capture from day one** (wrap arbitrary shell commands, not per-ecosystem dependency parsing), and they have **most of their free time available** right now (focused-sprint pace, not slow side-project pace).

This plan is the scaffolding + timeline to get a genuinely postable v0.1 — working `capture`/`verify` loop, tests, CI, README, demo — onto GitHub as fast as realistically possible without shipping vaporware.

## Step 0 (do this first, before Day 1)

1. Create `/Users/himanshu/projects/proofkit/` and copy this plan document into it (e.g. as `PLAN.md`) so it lives alongside the actual code from the start, rather than staying only in the hidden `~/.claude/plans/` location. All scaffolding in Day 1 below happens inside this directory.
2. `brew install node` — needed only to build/prove the second (Node.js) demo scenario below. **ProofKit itself stays a Python tool; this does not change the implementation language.** ProofKit is language-agnostic by design already — `capture` wraps an arbitrary shell command (`node app.js`, `go run main.go`, `ruby script.rb`, `npm test`, anything), so it works on any language's project the moment `subprocess.run` can invoke it. Installing Node here is purely so the demo/README can *prove* that claim with a real non-Python example instead of just asserting it.

## Cross-language demo (in addition to the Python demo in §5)

Alongside `demo/top_n_buggy.py`, add a matching Node.js bug so the README shows ProofKit working identically on two different languages with zero extra code — this is the concrete evidence for "targets developers in any language," not a marketing claim:

```javascript
// demo/top_n_buggy.js
function topN(items, n) {
  const sorted = [...items].sort((a, b) => b - a);
  return sorted[n];          // bug: should be sorted.slice(0, n)
}

const args = process.argv.slice(2).map(Number);
const n = args.pop();
console.log(topN(args, n));  // throws when result is undefined and used numerically downstream, or prints `undefined` — adjust to force a nonzero exit, e.g. by calling .toFixed() on the result
```
Demo transcript for the README, run right after the Python one:
```
proofkit capture -o bug.proof -- node demo/top_n_buggy.js 5 3 9 1 7 5
proofkit verify bug.proof   # STILL FAILING
# fix: sorted.slice(0, n)
proofkit verify bug.proof   # FIXED
```
This adds roughly 30–45 minutes to Day 5 (writing + verifying the JS demo alongside the Python one) — negligible timeline impact for meaningfully broader credibility.

## Naming note (flag before starting)

"ProofKit" is already an active, unrelated project (`proofsh/proofkit`, a TypeScript/FileMaker scaffolding tool, live at proofkit.dev). Different domain, unlikely to cause direct user confusion, but it does mean:
- The `proofkit.dev` domain and the "ProofKit" GitHub search results are already occupied by someone else's project — mild SEO/discoverability cost.
- **`proofkit` is free on PyPI** (verified: 404, unclaimed) — fine for now.
- Recommendation: proceed with the name for v0.1 (renaming later is cheap before you have real users), but don't get attached to it long-term without a 5-minute gut check once you're ready to publish to PyPI/promote publicly.

## MVP Feature List

**`proofkit capture -- <command> [args...]`**
- Runs the given argv via `subprocess.run(..., shell=False)` — never `shell=True`, so there's no shell-quoting inconsistency across machines. If the user needs shell features (`&&`, pipes), they wrap it themselves: `proofkit capture -- bash -c "cmd1 && cmd2"`.
- Captures: exit code, stdout/stderr, duration, timeout handling (default 120s, `--timeout` override), stdin=DEVNULL.
- If run inside a git repo: commit hash, branch, dirty/clean flag (via `git status --porcelain`) — no diff content in v1, just the boolean + hash.
- Platform info via stdlib `platform` (OS, arch, Python version).
- Env vars **not captured by default** (safe default). `--with-env` opts in, applying name-pattern redaction (`KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL`, `AUTH`, `ACCESS_KEY`, `PRIVATE` substrings → `<redacted>`), documented explicitly as "not a full secrets scanner."
- Packages everything into a portable `.proof` file — a plain zip (stdlib `zipfile`, no extra dependency) containing `manifest.json` + `stdout.txt` + `stderr.txt`. Inspectable with `unzip -l bug.proof` — transparency as a feature, not a black box.

**`proofkit verify <bug.proof>`**
- Unpacks the artifact, re-runs the **exact same argv** in the current working directory (`--cwd` to override).
- Compares captured vs replayed: exit code, and whether the captured stderr's "signature" (last non-empty line — reliably the `SomeError: message` line of a traceback) still appears in the replay.
- Verdict: **STILL FAILING** / **FIXED** / **CHANGED — needs manual review** — always prints the full captured-vs-replayed exit code + stderr tail alongside the verdict, so it's never an opaque black box.
- **Critical guardrail**: before replaying, compares the current git commit to the one recorded in the manifest. If identical, prints a loud warning (you're "verifying" against unchanged code) unless `--allow-same-commit` is passed. This is what makes the "catch the agent" demo trustworthy rather than theater — without it, verify could falsely look meaningful even when nothing changed.

**Explicitly cut from v1** (all reasonable v0.2+ additions once there are real users): sandboxing, minimization/delta-debugging, open proof-format spec, GitHub Action integration, streaming/live output during capture, stdin capture/replay, multi-step command orchestration, value-based secret scanning (entropy/token-prefix detection), path rewriting for cross-machine portability, Windows support, PyPI publishing automation, rich TUI/colored diffing beyond basic ANSI red/green.

**Known, honest limitation to state up front in the README, not discover later**: the verdict is a heuristic (exit code + last stderr line), not a full functional check. An agent that "fixes" a crash by wrapping it in `try/except: return None` instead of correctly fixing the logic will make `verify` report FIXED even though the output is still wrong. Document this explicitly: "confirms the crash is gone, not that the feature is correct — pair with your test suite."

## Architecture

- **Packaging**: `pyproject.toml`, `hatchling` build backend, `src/` layout, single runtime dependency: **Click** (subcommand groups are far less boilerplate than argparse, professional `--help` output out of the box).
- **File layout**:
  ```
  proofkit/
  ├── pyproject.toml
  ├── LICENSE (MIT)
  ├── README.md
  ├── CONTRIBUTING.md
  ├── .gitignore
  ├── .github/workflows/ci.yml
  ├── src/proofkit/
  │   ├── __init__.py         # __version__
  │   ├── cli.py              # click group; capture/verify commands
  │   ├── runner.py           # run_command(argv, cwd, timeout) -> ExecutionResult
  │   ├── manifest.py         # schema + build/serialize
  │   ├── gitinfo.py          # collect_git_info(cwd)
  │   ├── redact.py           # SECRET_KEY_PATTERNS, redact_env()
  │   ├── packaging.py        # write/read .proof zip archive
  │   ├── compare.py          # compare(captured, replayed) -> Verdict
  │   └── platforminfo.py
  ├── tests/
  │   ├── test_manifest.py
  │   ├── test_redact.py
  │   ├── test_compare.py
  │   ├── test_packaging.py
  │   └── test_integration_e2e.py
  └── demo/
      ├── top_n_buggy.py
      ├── top_n_fixed.py
      └── README.md
  ```
- **Manifest schema** (`manifest.json` inside the zip): `proofkit_version`, `capture_id`, `created_at`, `command.argv`, `execution.{exit_code, duration_seconds, timed_out, launch_error}`, `output.{stdout_path, stderr_path, *_sha256, *_bytes, truncated, stderr_signature}`, `environment.{platform, env_captured, env_vars, redacted_keys}`, `git.{is_repo, commit_hash, branch, is_dirty}`, optional `note`.
- **Compare logic**: exit-code match + signature present → STILL FAILING; exit codes differ + signature absent → FIXED; anything else → CHANGED (manual review).

## Timeline

Honest estimate for solo, focused-sprint pace: **rough working `capture`→`verify` loop in ~2 focused days (12–16 hrs)**; **genuinely postable v0.1 (tests, CI, README, demo GIF, tagged release) in ~5–7 focused days (20–28 hrs)**.

| Day | Focus | Est. |
|---|---|---|
| 1 | Scaffolding: `pyproject.toml`, src layout, click group stubs, `.gitignore`, `LICENSE`, `git init`, first commit, `pip install -e .`, confirm `proofkit --help` works | 3–4h |
| 2 | Capture core: `runner.py`, `platforminfo.py`, `gitinfo.py`, `redact.py`, `manifest.py`; `capture` prints manifest JSON (no zip yet) | 4–5h |
| 3 | Packaging: `packaging.py` zip writer/reader; `capture` writes a real `.proof`; sanity-check with `unzip -l` | 2–3h |
| 4 | Verify + compare: `compare.py` verdict logic, same-commit warning guard, `verify` CLI with `--cwd`, colored pass/fail output | 4–5h |
| 5 | Build the demo scenario (below) + manual end-to-end run: capture buggy → verify (STILL FAILING) → swap in fix → verify (FIXED); fix rough edges | 2–3h |
| 6 | Automated tests (redact/compare/manifest/packaging round-trips + one subprocess-driven integration test) + `.github/workflows/ci.yml` (pytest on 3.9 + 3.12) | 4h |
| 7 | README (pitch, install, quickstart transcript, schema summary, explicit Limitations section), demo GIF (asciinema + `agg`, or screen capture + `gifski`), `CONTRIBUTING.md`, final commit, `v0.1.0` tag, `gh repo create` + push, `gh release create` | 3–4h |

## Repo Scaffolding Checklist

- `pyproject.toml`: hatchling backend, `dependencies = ["click>=8.1"]`, `[project.optional-dependencies] dev = ["pytest>=7.0"]`, `[project.scripts] proofkit = "proofkit.cli:main"`.
- `LICENSE`: MIT.
- `.gitignore`: standard Python (`__pycache__/`, `*.egg-info/`, `.venv/`, `dist/`, `build/`, `.pytest_cache/`, `*.proof`).
- `.github/workflows/ci.yml`: matrix Python 3.9 + 3.12, `pip install -e .[dev]`, `pytest`.
- `README.md`: lead with the pitch ("catch AI coding agents' false 'I fixed it' claims"), install, quickstart transcript from a *real* run, manifest fields summary, explicit **Limitations** section, roadmap, contributing link.
- `CONTRIBUTING.md`: stub — how to run tests, PR expectations.
- **Before first commit**: this environment's global `git config user.name`/`user.email` is currently unset — decide and set the public-facing identity/email you want attached to open-source commits (likely not `himanshu.k@bandhantech.com` if this is a personal project) before running `git commit`.

**`gh` commands** (from inside the new `proofkit/` directory, after `git init` + first commit):
```bash
git branch -M main
gh repo create proofkit --public --source=. --remote=origin \
  --description "Catch false 'I fixed it' claims from AI coding agents — capture a bug once, verify the fix anywhere." \
  --push
# once README/tests/CI/demo GIF are in:
git tag v0.1.0
git push origin v0.1.0
gh release create v0.1.0 --generate-notes
```
Alternative: create as `--private` through day 6, flip to public (`gh repo edit --visibility public`) right before tagging the release, if a public WIP history isn't wanted.

**Repo was created private on day 1, per that alternative.** Branch protection on `main` (require PR + 1 approval before merge, admins can bypass) was attempted immediately but **GitHub blocks branch protection on private repos on the free plan** — it only becomes available once the repo is public (or on a paid plan). Contribution scaffolding (`.github/PULL_REQUEST_TEMPLATE.md`, `CONTRIBUTING.md`) is already in place; the actual protection rule must be applied via API right after flipping to public:
```bash
gh repo edit Himanshukurrey/proofkit --visibility public
gh api -X PUT repos/Himanshukurrey/proofkit/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f "required_status_checks=null" \
  -F "enforce_admins=false" \
  -f "required_pull_request_reviews[required_approving_review_count]=1" \
  -f "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -F "restrictions=null" \
  -F "allow_force_pushes=false" \
  -F "allow_deletions=false"
```
`enforce_admins=false` means the repo owner can still push/merge directly if needed; external contributors are forced through PR + review.

## Demo Scenario

A genuine off-by-one bug, small enough for the README, that crashes cleanly (nonzero exit) so exit-code comparison is the clean primary signal:

```python
# demo/top_n_buggy.py
def top_n(items, n):
    sorted_items = sorted(items, reverse=True)
    return sorted_items[n]          # bug: should be sorted_items[:n]

if __name__ == "__main__":
    import sys
    *item_args, n_arg = sys.argv[1:]
    items = [int(x) for x in item_args]
    print(top_n(items, int(n_arg)))
```
`python demo/top_n_buggy.py 5 3 9 1 7 5` → `IndexError`, exit 1. Narrative for the README/GIF:
```
proofkit capture -o bug.proof -- python demo/top_n_buggy.py 5 3 9 1 7 5
# (ask a coding agent to "fix the crash in top_n_buggy.py")
proofkit verify bug.proof
```

## Verification

- After Day 4: manually run the demo capture/verify loop end-to-end and confirm all three verdicts are reachable (STILL FAILING before any fix, FIXED after correcting the slice, CHANGED after introducing a different unrelated error) — this is the functional proof the tool works before writing a single automated test.
- Day 6: `pytest` green locally on Python 3.9, then push and confirm the GitHub Actions matrix (3.9 + 3.12) goes green on the actual repo.
- Before tagging `v0.1.0`: fresh-clone the repo into a throwaway directory, `pip install -e .`, and re-run the full demo transcript from the README verbatim — this catches any "works on my machine" gaps in the instructions themselves, which would be a bad first impression for a tool whose entire pitch is trustworthy reproduction.
