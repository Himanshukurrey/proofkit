# Security Policy

## Supported Versions

ProofKit is pre-1.0 (currently `0.1.0`). There's no version support matrix yet — only the latest release on `main` gets fixes.

## Reporting a Vulnerability

Please **don't open a public GitHub issue** for a security vulnerability. Instead, use [GitHub's private vulnerability reporting](https://github.com/Himanshukurrey/proofkit/security/advisories/new) for this repository, or open a regular issue asking to be contacted privately if that isn't available to you.

Include what you'd include in any good bug report: the affected version/commit, steps to reproduce, and the impact you think it has.

Given this is currently a solo-maintained, pre-1.0 project, please allow a few days for a first response rather than expecting an SLA.

## What's actually in scope

Worth knowing before reporting: ProofKit `capture`/`verify` run commands directly on your machine, exactly like typing them yourself — there's no sandboxing (see the README's Limitations section). Running arbitrary/untrusted commands through `proofkit capture` is not a vulnerability in ProofKit; it's the same trust boundary as running that command any other way. Genuine security issues would be things like: the `.proof` archive format being exploitable on read (e.g. a malicious zip triggering unintended behavior in `verify`), or `--with-env` redaction failing to redact something it claims to.
