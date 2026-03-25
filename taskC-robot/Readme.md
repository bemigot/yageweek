# The Robotic Stairclimber

A robot is standing at the bottom of a staircase (Step $0$) and needs to reach the top (Step $n$).
However, many steps are broken; the robot can only land on "good" steps.

### **Input**
* **Line 1:** Two integers $n$ and $k$ ($1 \le n \le 10^5$, $0 \le k < n$), representing the target step and the number of good steps between Step $0$ and Step $n$.
* **Line 2:** A sorted list of $k$ integers $v_1, v_2, \dots, v_k$ representing the indices of the good steps ($1 \le v_i < n$).

### **Rules**
* **Movement:** From any step $i$, the robot can perform a **Single Step** ($i \to i+1$) or a **Double Step** ($i \to i+2$).
* **Safety:** The robot cannot land on broken (non-good) steps. Step $0$ and Step $n$ are always considered good.
* **Path:** The path is represented as a sequence of movements: `1` for a single step, `2` for a double step.

### **Goal**
Find a path from Step $0$ to Step $n$ that uses the **minimum total number of movements**.
If there are multiple paths with the same minimum length, choose the one that is **lexicographically smallest** 
(e.g., prefer `112` to `121`).

### **Output**
* **Line 1:** The minimum number of movements required to reach Step $n$. If the top is unreachable, output `-1`.
* **Line 2:** The sequence of movements (e.g., `212`) that satisfies the goal.

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
- for {1,2} sequences of the same length relation "lexicographically smaller"
  is equivalent to "numerically smaller"
- looks like this is a Dynamic Programming problem: we should start
  from the finish step, and move backwards, dropping unreachable paths
- we can build a table (let's call it `dp`) where dp[i] stores
  the minimum number of movements to reach *n* from step *i*.
  1. Shortest Path: For each good step *i*, distance is simply 1 + min(dp[i+1], dp[i+2])
  2. Lexicographical Priority: When we eventually move forward from 0 to reconstruct the path:
     - If we are at step *i* and *dp[i+1] ≤ dp[i+2]*, we make a *Single step* - 1.
     - Because the total path lengths are equal (or i+1 is even shorter),
       starting with a 1 automatically guarantees a numerically
       (and thus lexicographically) smaller sequence.
- "Drop Unreachable" Strategy: by initializing `dp` table with "infinity" (10^6),
  any step that cannot reach the finish remains marked "infinity".
  - If dp[0] ends up being "infinity", we immediately know the task is impossible (output -1)
  - This naturally handles "dead ends" where broken steps create a "gap" larger than 2
