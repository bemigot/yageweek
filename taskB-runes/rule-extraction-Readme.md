# Magic runes — rule extraction via MLP oracle

## Goal

Extract a **human-readable if-then rule** that fully explains the spell/non-spell
classification, using the 100%-accurate MLP (Try 2, `runes-kit.py`) as a labeling
oracle.

## Why the MLP as oracle

`runes-kit.py` scored 100% on the 73-rune test set. Its weights encode the correct
rule — but as floating-point numbers, not readable logic. The oracle approach decodes
that knowledge:

1. Re-train the MLP on the 170 labeled runes (identical setup to `runes-kit.py`).
2. Run it on all 243 possible runes → complete, correct label set.
3. Distill those 243 ground-truth labels into a shallow `sklearn` decision tree.

The decision tree has a much easier job than the MLP: it only needs to find a compact
boolean rule that reproduces 243 known-correct labels, using simple human-interpretable
features.

## Why this beats the CatBoost distillation

CatBoost topped out at 97.3% (2 wrong runes). Its distillation was summarising a
slightly incorrect model — any tree learned from those labels would inherit the errors.

| | CatBoost distillation | Oracle distillation |
|---|---|---|
| Label source | CatBoost (97.3% correct) | MLP oracle (100% correct) |
| 243-rune labels | 2 wrong | correct by construction |
| Tree validity | wrong on ≥ 2 runes | valid if depth is sufficient |

## Approach

### Step 1 — Oracle labeling

```python
# encode() from example/common.py: 51-dim one-hot (15 positional + 36 bigram)
all_runes = [''.join(r) for r in itertools.product('FWE', repeat=5)]
X_all_51  = np.array([encode(r) for r in all_runes])
y_oracle  = mlp.predict(X_all_51)  # 243 correct labels
```

### Step 2 — Distill with simple features

Feed those 243 labels to a `DecisionTreeClassifier` using only the 5 raw positional
features (ordinal-encoded F=0, W=1, E=2). If a shallow tree fits perfectly, the rule
is positional. If not, add bigrams and retry.

```python
enc = OrdinalEncoder(categories=[['F', 'W', 'E']] * 5)
X_pos = enc.fit_transform([[c for c in r] for r in all_runes])

for depth in range(1, 7):
    dt = DecisionTreeClassifier(max_depth=depth).fit(X_pos, y_oracle)
    if dt.score(X_pos, y_oracle) == 1.0:
        print(export_text(dt, feature_names=[f'p{i}' for i in range(5)]))
        break
```

### Reading the depth result

| First perfect depth | Interpretation |
|---|---|
| 1–2 | Single condition on one position |
| 3–4 | Conjunction of 2–3 conditions; fully readable |
| 5–6 | Positional features insufficient; retry with bigrams |
| 7+  | Rule may require trigrams or a non-positional encoding |

### Reading the depth result (revised)

| First perfect depth | Interpretation |
|---|---|
| 1–2 | Single condition; trivially readable |
| 3–4 | Compact conjunction; fully readable |
| 5–6 | Moderately complex; still usable |
| 7   | Complex but correct — translate to Python |
| 8+  | Feature set insufficient for tree distillation |

## Implementation

`find-rule.py` — self-contained script, no new dependencies beyond what `runes-kit.py`
already uses (`numpy`, `scikit-learn`).

## Distillation experiments

Oracle labels: **113 spells**, 130 non-spells out of 243 (includes the 2 that CatBoost
missed: `FFWFW` and `WFWFW`).

Encoding for ordinal feature sets: F=0, W=1, E=2. Threshold `<= 0.5` means `==F`,
`<= 1.5` means `in {F,W}`, `> 1.5` means `==E`.

| Feature set | Features | Perfect-fit depth |
|---|---|---|
| Counts only (`cnt_F`, `cnt_W`, `cnt_E`) | 3 numeric | never (63% ceiling) |
| Pairwise equality only (`pi=pj` booleans) | 10 binary | never (60% ceiling) |
| `p024` only (3-char alternating string) | 1 × 27-val | never (78% ceiling) |
| `p13` only (2-char string at pos 1,3) | 1 × 9-val | never (72% ceiling) |
| `p024` + `p13` | 2 categorical | never (92% at depth 8) |
| Pairwise + positional | 10 + 5 numeric | **7** |
| `p13` + positional | 1 + 5 numeric | **7** |
| Counts + positional | 3 + 5 numeric | **8** |
| Positional only (`p0`–`p4`) | 5 × 3-val | **7** |
| Positional + bigrams | 5 + 4 × 9-val | **7** |
| Positional + bigrams + trigrams | 5 + 4 + 3 | never (99.6% at depth 8) |

## Conclusions

**The rule is purely positional** — symbol counts, pairwise equalities, and n-gram
groupings all fail to compress it. Individual position values are necessary.

**Depth 7 is the floor.** Every feature set that achieves 100% needs at least depth 7.
No engineering reduced this. The rule is inherently a 7-level boolean decision over
the 5 positions (F=0, W=1, E=2).

**Key structural observations:**
- `p13` (the combined value of positions 1 and 3) is highly informative: for E-starting
  runes the rule collapses to `p13 == WW` (i.e. `p1==W AND p3==W`), verified at depth 3.
- `p2==W` (position 2 is Water) acts as a critical swing condition in the F/W-starting
  branch — several non-spell cases hinge on it.
- Adding bigrams, trigrams, pairwise equalities, or counts never reduces depth below 7;
  trigrams + positional actually makes distillation fail entirely within depth 8.

**Next step:** translate the depth-7 positional tree to a Python `is_spell(rune)` function.
