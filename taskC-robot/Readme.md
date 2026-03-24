**Input** (all numbers separated by " "):
- line 1: n k (1<= n <=10^5, 0 <= k < n) - target tile, number of reliable tiles
- line 2: An ordered list of k integers representing
  the indices of intermediate reliable tiles.

**Goal**: Find a path from tile 0 to tile n using the minimum number of jumps.
If multiple paths have the same minimum number of jumps, choose the one
that is lexicographically smallest when the jumps are viewed as a sequence of integers.

**Rules**:
* Movement: From tile i, you can jump to tile i+1 or i+2.
* Safety: You can only land on "reliable" tiles. Tile 0 and tile n are always considered reliable.

**Output**:
1. Line 1: The minimum number of jumps (or −1 if impossible).
2. Line 2: The sequence of jump lengths (e.g., 212)
   that achieves this minimum and is lexicographically smallest.

**Example**
Input:
```
5 3
2 3 4
```
Output:
```
3
212
```

Ideas:
- lexicogrpahically smaller is equivalent to numerically
  smaller for {1,2} sequences of the same length
- this looks like a Dynamic Programming problem: we should start
  from the finish tile, and hop backwards, dropping unreachable paths
- we can build a table (let's call it dp) where dp[i] stores
  the minimum number of jumps to reach n from tile i.
  1. Shortest Path: For each reliable tile i, distance is simply 1 + min(dp[i+1], dp[i+2])
  2. Lexicographical Priority: When we eventually move forward from 0 to reconstruct the path:
     - If we are at tile i and dp[i+1] ≤ dp[i+2], we take the jump of 1.
     - Because the total path lengths are equal (or i+1 is even shorter),
       starting with a 1 automatically guarantees a numerically
       (and thus lexicographically) smaller sequence.
- "Drop Unreachable" Strategy: by initializing `dp` table with "infinity" (10^6),
  any tile that cannot reach the finish remains "infinity".
  - If dp[0] ends up being "infinity", we immediately know the task is impossible (output -1)
  - This naturally handles "dead ends" where unreliable tiles create a gap larger than 2
