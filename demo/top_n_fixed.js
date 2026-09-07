// The fix for top_n_buggy.js — reference version, not used by ProofKit itself.
//
// Usage: node top_n_fixed.js <item> <item> ... <n>

function topN(items, n) {
  const sorted = [...items].sort((a, b) => b - a);
  return sorted.slice(0, n); // fixed: slice, not index
}

const args = process.argv.slice(2).map(Number);
const n = args.pop();
const result = topN(args, n);
console.log(result.map((x) => x.toFixed(2)).join(", "));
