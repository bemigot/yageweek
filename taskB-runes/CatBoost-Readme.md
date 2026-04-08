# Magic runes — CatBoost approach

## Goal

Classify 5-symbol runes (symbols: F, W, E) as magical spells (1) or duds (0), and
**extract a human-readable rule** that explains the classification — not just a black-box
predictor.

## Why CatBoost

- **Native categorical support.** Each of the 5 positions takes one of 3 values
  (`F`, `W`, `E`). CatBoost ingests these directly; no one-hot encoding or manual
  feature engineering needed (contrast: the NumPy net required 15 input neurons just
  for positional one-hots, plus 36 bigram features).
- **Accurate on small datasets.** 170 labeled samples, 5 features, binary target —
  well within CatBoost's comfort zone; its built-in regularization prevents overfitting.
- **Tree-based internals.** Gradient boosting over decision trees produces a model
  whose learned splits can be inspected and distilled into explicit if-then rules.

## CPU feasibility

CatBoost is CPU-first; GPU support is optional. At this scale (170 rows, 5 features)
training completes in well under a second on any modern CPU. The GPU path exists for
datasets with millions of rows — it offers no advantage here.

## Approach

The search space is exhaustible: 3⁵ = **243 possible runes** in total, of which 170
are labeled. This opens a two-step distillation strategy:

### Step 1 — Train CatBoost and label all 243 runes

Train a CatBoostClassifier on the 170 labeled runes, then run inference on the complete
set of 243 possible runes. This produces a fully-labeled universe.

```python
import itertools, pandas as pd
from catboost import CatBoostClassifier

all_runes = pd.DataFrame(
    list(itertools.product('FWE', repeat=5)),
    columns=[f'p{i}' for i in range(5)]
)
all_runes['spell'] = model.predict(all_runes)
```

### Step 2 — Distill into a shallow decision tree

Fit a `sklearn` `DecisionTreeClassifier` (depth ≤ 4) on those 243 labeled points,
then print the tree as text. Because the underlying magic rule is presumably simple,
a shallow tree should reproduce it perfectly and make it readable.

```python
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OrdinalEncoder

enc = OrdinalEncoder(categories=[['F', 'W', 'E']] * 5)
X_all = enc.fit_transform(all_runes[[f'p{i}' for i in range(5)]])

dt = DecisionTreeClassifier(max_depth=4)
dt.fit(X_all, all_runes['spell'])
print(export_text(dt, feature_names=[f'p{i}' for i in range(5)]))
```

If the decision tree at depth 4 achieves 100 % accuracy on all 243 predictions, the
rule has been found. A depth that small and a perfect fit together imply the rule is
genuinely simple.

### Success criterion

A depth-≤-4 decision tree that perfectly reproduces CatBoost's labeling of all 243
runes, yielding a concise, human-readable if-then ruleset.

## Try 1: positional features only — 95.9% (3 wrong)

Features: 5 positional categorical columns (`p0`–`p4`), raw `F`/`W`/`E` values.

```
Train accuracy:       100.0%
answers.csv accuracy:  95.9%  (70/73 correct)
Spells found:         110/243
```

**Problems:**
- Same 3 misclassifications as the original 1-hidden-layer NumPy net (Try 1 in Readme.md).
  The hard cases apparently require knowledge of adjacent-symbol interactions.
- Distillation failed: the decision tree never reached 100 % even at depth 6 (97.1 %),
  confirming the underlying rule involves inter-position structure that positional
  features alone cannot express.

**Conclusion:** positional features are insufficient. The rule encodes relationships
between adjacent symbols (the bigram features in Try 2 of the NumPy approach were what
fixed the 3 misclassifications). Next: add n-gram features.

## Try 2: positional + trigrams — 97.3% (2 wrong)

Features: 5 positional + 3 trigram + 1 alternating (`p0p2p4`) = 9 total.

```
Train accuracy:       100.0%
answers.csv accuracy:  97.3%  (71/73 correct)
Spells found:         111/243
Distillation:         100% at depth 8 (memorisation, not a rule)
```

Improvement over Try 1 (fixed 1 of 3 errors) but distillation tree is unreadable —
opaque numeric trigram indices (`t012 <= 15.50`) convey nothing without a lookup table.

## Try 3: positional + bigrams — 97.3% (2 wrong)

Features: 5 positional + 4 bigram = 9 total. Mirrors the feature set that gave the
NumPy neural net 100%.

```
Train accuracy:       100.0%
answers.csv accuracy:  97.3%  (71/73 correct)
Spells found:         111/243
Distillation:         100% at depth 6
```

Same 2 wrong runes as Try 2: `WFWFW` and `FFWFW` (both false negatives).

**Root cause identified:** both wrong runes have `b34=FW` and `b23=WF`. Every spell
in the training set with `b34=FW` also has `b23=FF`. CatBoost learned the conjunction
`b23=FF AND b34=FW → spell` and cannot generalize to `b34=FW` alone. The MLP neural
net did generalize correctly because it learns smooth continuous boundaries rather than
axis-aligned tree splits.

## Try 4: bigrams only + hyperparameter tuning — 97.3% (2 wrong)

Dropped trigrams and `p024`; tuned to `depth=3, iterations=2000, lr=0.05`.
No change — the ceiling is structural, not a hyperparameter problem.

## Conclusion

**CatBoost tops out at 97.3% on this dataset.** The 2 stubborn misclassifications stem
from a training-data coverage gap: no labeled spell has `b34=FW AND b23≠FF`, so
CatBoost cannot bridge that gap regardless of features or tuning. Gradient boosted trees
do not extrapolate across unseen feature conjunctions; MLPs do.

The distillation goal (human-readable rule at depth ≤ 4) was also not met — the
best result was depth 6 with bigram index thresholds that require a lookup table to
interpret.

**CatBoost is not the right tool for rule extraction on this dataset.**
