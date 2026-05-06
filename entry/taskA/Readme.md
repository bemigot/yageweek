**Input** (all numbers separated by " "):
- line 1: n q (1<= n, q <=10^5)
- line 2: n integer "weights" (1 <= w[i] <= 10^8) - array **w**
- lines 3..2+q: l r (1 <= l <= r <= n)

For each l,r sum up w_optimal[l-1]..w_optimal[r-1] = W_qth

**Output**: sum of all W_qth sums

*w_optimal* - contains all original **w** elements, reorganized to maximize **Output**

The idea:
- sort **w** in-place high-to-low
- iterate over lines 3..2+q and count number of entries (popcount) for each w_optimal element,
  put popcounts in popcount[] array
- for largest popcount[i1] choose the largest w[j] and put that in w_optimal[i].
  Increment j, choose the next largest popcount[i2].
  *Open question*: how to iterate over popcount[] not by index, but in
  decreasing order of popcounts?
- count **Output**

See [comments / answer](task1comment.md) and [solution](Sol1.java)

**Example 1**
Input:
```
3 4
7 3 1
1 3
2 3
3 3
2 2
```
Output: 31

**Example 2**
Input:
```
4 4
1 100 10000 10101010
1 4
2 3
2 2
1 2
```
Output: 40424241
