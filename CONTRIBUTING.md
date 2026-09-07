# Contributing to ProofKit

Thanks for considering a contribution. Here's the workflow.

## How to contribute

1. **Fork the repo** and clone your fork locally.
2. **Create a branch** for your change: `git checkout -b fix/short-description`.
3. **Make your change**, with tests if you're changing behavior.
4. **Run the test suite** locally before opening a PR:
   ```bash
   pip install -e ".[dev]"
   pytest
   ```
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
