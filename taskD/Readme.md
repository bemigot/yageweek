# Minimize sum of moduli

Goal from a n-by-m matrix of non-negative integers, choose one number
*a* from each row, and put them in a sequence, so that sum of
absolute differences between neighboring members is at the minimum.

$|a_2 - a_1| + |a_3 -a_2| + \dots + |a_n - a_n-1|$

Print the chosen numbers $a_1, a_2, \dots, a_n$

If there are multiple sequences satisfying the minimum condition,
print the one with the minimum sum of those numbers.

**Input**
* **Line 1:** Two integers $n$ and $m$ ($1 \le n * m \le 10^5$), $n$ -
  number of rows, $m$ - numbers in a row
* **Line 2..$n+1$**: $m$ integers $a_i$ ($1 \le a_i \le 10^9$)

**Output**: sorted sequence of numbers, separated by space.

**Example Input**:
```
3 2
2 2
6 7
99 1
```

**Example Output**: `1 2 6`
      
