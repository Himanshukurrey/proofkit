# Contributing to ProofKit

Thanks for considering a contribution. Here's the workflow.

## How to contribute

1. **Fork the repo** and clone your fork locally.
2. **Create a branch** for your change: `git checkout -b fix/short-description`.
3. **Make your change**, with tests if you're changing behavior.
4. **Run the test suite and linter** locally before opening a PR:
   ```bash
   pip install -e ".[dev]"
   pytest
   ruff check .
   ruff format --check .
   ```
   CI runs the same checks across Linux, Windows, and macOS, on Python 3.9 and 3.12 — matching locally first saves a round trip.
5. **Open a pull request** against `main`. Fill in the PR template — what the change does, why, and how you tested it.
6. A maintainer will review it. Please be patient; this is currently maintained part-time.

## Why PRs go through review

`main` is protected — nobody (including the maintainer, in most cases) pushes directly to it. Every change lands through a reviewed pull request. This isn't about distrust; it's so the project has a consistent, auditable history and a second pair of eyes on every change, from day one.

## What makes a good PR

- **Small and focused.** One logical change per PR is much easier to review than five unrelated fixes bundled together.
- **Tested.** If you fixed a bug, a regression test that would have caught it is the strongest evidence the fix is real.
- **Explained.** A one-line "fixed the bug" isn't enough — say what was broken and why your change addresses it.

## Reporting bugs

Open an issue describing what you expected vs. what happened, your OS/Python version, and the exact command you ran. If you have ProofKit installed already, `proofkit capture -- <the failing command>` and attaching the resulting `.proof` file is the fastest way to get a bug looked at — it's exactly the problem this project exists to solve.

## Code of conduct

Be respectful. Disagreements about code are fine; personal attacks aren't.

## Releasing (maintainer only)

1. Bump `version` in `pyproject.toml`.
2. `git tag vX.Y.Z && git push origin vX.Y.Z`
3. `gh release create vX.Y.Z --generate-notes`

Publishing that release automatically triggers `.github/workflows/release.yml`, which builds the package, sanity-checks that the wheel actually installs and `proofkit --version` runs, and publishes to PyPI via [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no stored API token).

**One-time setup required before this works for the first time**, done once on pypi.org by whoever owns the PyPI project: create a PyPI account if needed, then add a "pending publisher" for a project named `proofkit` under Account Settings → Publishing, with:
- Owner: `Himanshukurrey`
- Repository: `proofkit`
- Workflow name: `release.yml`
- Environment name: `pypi`

This reserves the trust relationship before the package exists on PyPI, so the very first `gh release create` can publish successfully rather than needing a manual first upload.
