// Deliberately buggy: off-by-one, same shape of bug as top_n_buggy.py — used
// to prove ProofKit is language-agnostic (it just wraps a shell command).
//
// Usage: node top_n_buggy.js <item> <item> ... <n>

function topN(items, n) {
  const sorted = [...items].sort((a, b) => b - a);
  return sorted[n]; // bug: should be sorted.slice(0, n)
}

const args = process.argv.slice(2).map(Number);
const n = args.pop();
const result = topN(args, n);
console.log(result.toFixed(2)); // throws when result is undefined (n out of bounds)
