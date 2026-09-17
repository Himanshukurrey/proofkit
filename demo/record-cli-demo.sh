#!/bin/bash
# Records demo/proofkit-demo.gif — the CLI-only capture/verify/fix/verify story.
#
# Prerequisites: asciinema and agg (brew install asciinema agg), proofkit
# installed and on PATH, and run from a clean checkout of this repo (demo/
# top_n_buggy.py must still have the bug — it always should).
#
# Usage:
#   asciinema rec --command "bash demo/record-cli-demo.sh" --overwrite \
#     --window-size 100x28 --idle-time-limit 3 /tmp/proofkit-demo.cast
#   agg --theme dracula --font-size 16 --idle-time-limit 3 \
#     /tmp/proofkit-demo.cast demo/proofkit-demo.gif
#
# This script makes a REAL git commit during recording (to demonstrate the
# fix), which must be reset afterward:
#   git reset --hard HEAD~1 && rm -f bug.proof

set -e
export TERM=xterm-256color
clear

show() { printf '\033[1;32m$\033[0m %s\n' "$1"; sleep 0.4; }

show "proofkit capture -o bug.proof -- python demo/top_n_buggy.py 5 3 9 1 7 5"
proofkit capture -o bug.proof -- python demo/top_n_buggy.py 5 3 9 1 7 5
sleep 2.5

show "proofkit verify bug.proof"
proofkit verify bug.proof || true
sleep 3

show "# an AI agent applies a fix and commits it"
sleep 0.8
show "sed -i '' 's/sorted_items\[n\]/sorted_items[:n]/' demo/top_n_buggy.py"
sed -i '' 's/sorted_items\[n\]/sorted_items[:n]/' demo/top_n_buggy.py
sleep 0.5
show "git commit -am 'Fix off-by-one: slice instead of index'"
git commit -am 'Fix off-by-one: slice instead of index'
sleep 1.5

show "proofkit verify bug.proof"
proofkit verify bug.proof || true
sleep 3
