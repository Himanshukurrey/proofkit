# ProofKit demo

Two equivalent off-by-one bugs, one in Python and one in Node.js, used to
show that ProofKit doesn't care what language the command is written in —
it just captures and replays whatever you give it.

## Python

```bash
proofkit capture -o bug.proof -- python demo/top_n_buggy.py 5 3 9 1 7 5
# (ask a coding agent to fix the crash in top_n_buggy.py, or apply the fix
# from top_n_fixed.py yourself)
proofkit verify bug.proof
```

## Node.js

```bash
proofkit capture -o bug.proof -- node demo/top_n_buggy.js 5 3 9 1 7 5
proofkit verify bug.proof
```

Both bugs are the same mistake: indexing a sorted array (`sorted[n]`) instead
of slicing it (`sorted[:n]` / `sorted.slice(0, n)`). The fixed versions
(`top_n_fixed.py`, `top_n_fixed.js`) show the correct version, for reference
— they aren't used by ProofKit itself.

## Demo GIFs

The three GIFs in this directory (`proofkit-demo.gif`, `proofkit-claude-code-demo.gif`, `proofkit-install-demo.gif`) are real recordings, not mockups — captured with [asciinema](https://asciinema.org/) and rendered with [agg](https://github.com/asciinema/agg) (`brew install asciinema agg`). Each has a matching `record-*.sh` script here for reproducing it; see the comment header in each script for exact prerequisites and the `asciinema rec` / `agg` invocations.
