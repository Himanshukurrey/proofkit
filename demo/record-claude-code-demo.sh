#!/bin/bash
# Records demo/proofkit-claude-code-demo.gif — Claude Code auto-invoking the
# proofkit skill on a plain bug report, no mention of ProofKit by name.
#
# Prerequisites: asciinema, agg, the claude CLI, and the proofkit plugin
# genuinely installed (not --plugin-dir) via:
#   claude plugin marketplace add Himanshukurrey/proofkit
#   claude plugin install proofkit@proofkit --scope user
#
# --dangerously-skip-permissions is required here specifically because
# allowed-tools pre-approval does not apply in non-interactive (-p) mode —
# see the README Limitations section and issue #6. Normal interactive usage
# does not need this flag (confirmed separately in PR #4).
#
# Usage:
#   asciinema rec --command "bash demo/record-claude-code-demo.sh" \
#     --overwrite --window-size 100x24 --idle-time-limit 3 \
#     /tmp/proofkit-claude-code-demo.cast
#   agg --theme dracula --font-size 16 --idle-time-limit 3 \
#     /tmp/proofkit-claude-code-demo.cast demo/proofkit-claude-code-demo.gif
#
# Clean up afterward: rm -rf .proofkit *.proof

set -e
export TERM=xterm-256color
clear

show() { printf '\033[1;32m$\033[0m %s\n' "$1"; sleep 0.4; }

show "claude -p 'There is a bug: running python demo/top_n_buggy.py 5 3 9 1 7 5 crashes. Capture this bug using proofkit before doing anything else, then briefly report what you did.' --dangerously-skip-permissions"
claude -p 'There is a bug: running python demo/top_n_buggy.py 5 3 9 1 7 5 crashes. Capture this bug using proofkit before doing anything else, then briefly report what you did.' --dangerously-skip-permissions
sleep 3
