## **Minimize Sum of Absolute Differences**

**Goal**
Given an $n \times m$ matrix of non-negative integers, select exactly one
integer from each row. Let this collection of $n$ integers be your set.
Your objective is to choose the set such that, when its elements are arranged
in an optimal order, the sum of absolute differences between adjacent members
is minimized.

Specifically, if your chosen numbers are
$\{a_1, a_2, \dots, a_n\}$, you want to minimize:
$$\min_{\text{permutations } \sigma} \sum_{i=1}^{n-1} |a_{\sigma(i+1)} - a_{\sigma(i)}|$$

*(Note: This sum is minimized when the chosen numbers are arranged in
ascending order, reducing the formula to $\max(a_i) - \min(a_i)$.)*

**Tie-breaking Rule**
If multiple sets yield the same minimum sum of absolute differences,
choose the set that has the **minimum total sum** of its elements ($\sum a_i$).

**Input**
* **Line 1**: Two integers $n$ and $m$ ($1 \le n \times m \le 10^5$),
  where $n$ is the number of rows and $m$ is the number of elements per row.
* **Lines 2 to $n+1$**: $m$ integers ($1 \le p_i \le 10^9$) representing the elements of each row.

**Output**
* Print the $n$ chosen numbers in **ascending order**, separated by spaces.

**Example Input**
```
3 2
2 2
6 7
99 1
```

**Example Output**
```
1 2 6
```

## Ideas
* Since we are free to reorder row "representatives", i.e. treat them
  as a *set* (where you pick the numbers and then arrange them),
  the minimum sum of absolute differences is always achieved by sorting those
  numbers in ascending order.
* Moreover, by sorting them in ascending order, we can calculate the target
  metric as $a_n - a_1$.
* We can flatten this matrix: put all numbers in a single row, though we should  keep track of their origin row - the "color".
* As soon as all numbers are arranged in order, we can apply "sliding windows"
  approach, and shrink the window, just keeping eye on having at least
  one of each "color". That probably warrants adding a vector
  of counters for each row ("color") representatives in a "window".

## Review

**Standalone min-sum (ignoring diff):**
Trivial — just pick the minimum element from each row.
Sum = $\sum \min(\text{row}_i)$.

**How the tie-break integrates with the sliding window:**

Each valid window $[L, R]$ in the sorted flat array
(containing $\ge 1$ element per row) represents a candidate solution.
For that window, the best possible sum is achieved by picking
the **smallest element of each row within the window** — which is
its leftmost occurrence in the sorted array.

So for each valid window we track two costs lexicographically:
* $\text{range} = \text{arr}[R] - \text{arr}[L]$ — the primary diff cost
* $\text{sum} = \sum (\text{leftmost element of each row in current window})$ — the tie-break cost

**Maintaining sum incrementally:**
When the left pointer $L$ advances past a row's element, that row's
representative shifts to the next element in the window.
The sum increases by exactly that difference.
This keeps the update O(1) per step.

**Combined algorithm:** slide the window, maintain
$(\text{range}, \text{sum})$ for each valid window, and track
the global minimum pair lexicographically.

This remains $O(N \log N)$ overall — the tie-break adds no extra complexity.
