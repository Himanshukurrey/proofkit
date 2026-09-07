"""Deliberately buggy: off-by-one in the slice, used as the running demo for ProofKit.

Usage: python top_n_buggy.py <item> <item> ... <n>
The last argument is n; everything before it is the list of items.
"""
import sys


def top_n(items, n):
    sorted_items = sorted(items, reverse=True)
    return sorted_items[n]  # bug: should be sorted_items[:n]


if __name__ == "__main__":
    *item_args, n_arg = sys.argv[1:]
    items = [int(x) for x in item_args]
    print(top_n(items, int(n_arg)))
