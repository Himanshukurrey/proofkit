#!/bin/bash
# Records demo/proofkit-install-demo.gif — a genuinely fresh `pip install
# proofkit` from real PyPI, then a real capture/verify run, in a directory
# that is deliberately NOT a git repo (so verify's same-commit guardrail
# doesn't apply — kept simple on purpose; the CLI demo covers that guardrail).
#
# Prerequisites: asciinema, agg. Run this INSIDE the fresh directory/venv
# described below — it is not meant to run against this repo's own checkout.
#
# Setup (not recorded):
#   mkdir -p /tmp/proofkit-install-demo && cd /tmp/proofkit-install-demo
#   python3 -m venv .venv && source .venv/bin/activate
#   pip install -q --upgrade pip   # avoids a distracting "pip is outdated" warning
#   cat > bug.py << 'EOF'
#   def top_n(items, n):
#       sorted_items = sorted(items, reverse=True)
#       return sorted_items[n]  # bug: should be sorted_items[:n]
#
#   if __name__ == "__main__":
#       import sys
#       *item_args, n_arg = sys.argv[1:]
#       items = [int(x) for x in item_args]
#       print(top_n(items, int(n_arg)))
#   EOF
#
# Usage (from inside that directory, with the venv active):
#   asciinema rec --command "bash /path/to/record-install-demo.sh" \
#     --overwrite --window-size 100x28 --idle-time-limit 3 \
#     /tmp/proofkit-install-demo.cast
#   agg --theme dracula --font-size 16 --idle-time-limit 3 \
#     /tmp/proofkit-install-demo.cast demo/proofkit-install-demo.gif

set -e
export TERM=xterm-256color
clear

show() { printf '\033[1;32m$\033[0m %s\n' "$1"; sleep 0.4; }

show "pip install proofkit"
pip install proofkit
sleep 1.5

show "proofkit --version"
proofkit --version
sleep 1.5

show "proofkit capture -o bug.proof -- python bug.py 5 3 9 1 7 5"
proofkit capture -o bug.proof -- python bug.py 5 3 9 1 7 5
sleep 2

show "proofkit verify bug.proof"
proofkit verify bug.proof || true
sleep 3
