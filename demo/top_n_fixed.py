"""The fix for top_n_buggy.py — reference version, not used by ProofKit itself.

Usage: python top_n_fixed.py <item> <item> ... <n>
"""

import sys


def top_n(items, n):
    sorted_items = sorted(items, reverse=True)
    return sorted_items[:n]  # fixed: slice, not index


if __name__ == "__main__":
    *item_args, n_arg = sys.argv[1:]
    items = [int(x) for x in item_args]
    print(top_n(items, int(n_arg)))
