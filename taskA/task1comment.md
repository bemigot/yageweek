### Task clarity
Clear. Rearrange weights to maximize the total sum across all range queries, then output that total.

### Algorithm soundness
Correct. This is the rearrangement inequality — pair the largest weight with the most-queried position.

Verified against both examples:

Example 1: popcounts = [1, 3, 3] → sorted [3,3,1]; w sorted [7,3,1]

  → 7×3 + 3×3 + 1×1 = 31 ✓

Example 2: popcounts = [2,4,2,1] → sorted [4,2,2,1]; w sorted [10101010,10000,100,1]

  → 10101010×4 + 10000×2 + 100×2 + 1×1 = 40424241 ✓

**Answer to the open question**: You don't need to track which index had which popcount —
just sort popcount[] descending independently, then dot-product with
sorted w[]. The rearrangement inequality guarantees this pairing is optimal.

One gap to address: Computing popcounts naively (increment every position l..r per query)
is O(n·q) = 10^10 — too slow. Use a difference array:
```
  for each query (l, r):
      diff[l] += 1
      diff[r+1] -= 1
  popcount[i] = prefix_sum(diff)[i]
```
  This is O(n + q).

  Final algorithm:
  1. Sort w descending
  2. Build popcount[] via difference array + prefix sum — O(n+q)
  3. Sort popcount[] descending
  4. Output = Σ w[i] × popcount[i]

### A few notes on the implementation:

- Uses BufferedReader/StringTokenizer for fast I/O (important at q=10^5)
- Both w and popcount are sorted ascending and read together — largest×largest without a reverse pass
- result is long; max value is ~10^8 × 10^5 × 10^5 = 10^18, which fits in a long
