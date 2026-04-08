#!/usr/bin/env python3
"""Rune spell detector — CatBoost edition.

Strategy:
  1. Train CatBoostClassifier on 170 labeled runes (raw F/W/E, no encoding).
  2. Label all 243 possible runes.
  3. Distill into a shallow sklearn DecisionTree → human-readable rule.
"""

import itertools
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OrdinalEncoder

SYMBOLS = ['F', 'W', 'E']
POS = [f'p{i}' for i in range(5)]

# --------------------------------------------------------------------------- #
# Data loading                                                                 #
# --------------------------------------------------------------------------- #

def load_labeled(path):
    df = pd.read_csv(path)
    for i, col in enumerate(POS):
        df[col] = df['rune'].str[i]
    return df[POS], df['spell'].astype(int)


def load_unlabeled(path):
    df = pd.read_csv(path)
    for i, col in enumerate(POS):
        df[col] = df['rune'].str[i]
    return df[POS], df['rune']


# --------------------------------------------------------------------------- #
# Train                                                                        #
# --------------------------------------------------------------------------- #

X_train, y_train = load_labeled('train_runes.csv')
n_spell = y_train.sum()
print(f"Training on {len(y_train)} runes  ({n_spell} spells, {len(y_train) - n_spell} non-spells)")

model = CatBoostClassifier(
    iterations=300,
    depth=6,
    cat_features=POS,
    verbose=False,
    random_seed=42,
)
model.fit(X_train, y_train)

train_acc = (model.predict(X_train).astype(int) == y_train.values).mean()
print(f"Train accuracy: {train_acc:.1%}")

# --------------------------------------------------------------------------- #
# Evaluate against answers.csv                                                 #
# --------------------------------------------------------------------------- #

X_ans, ans_runes = load_unlabeled('answers.csv')
y_ans_true = pd.read_csv('answers.csv')['spell'].astype(int).values
y_ans_pred = model.predict(X_ans).astype(int)
ans_acc = (y_ans_pred == y_ans_true).mean()
print(f"answers.csv accuracy: {ans_acc:.1%}  ({(y_ans_pred == y_ans_true).sum()}/{len(y_ans_true)} correct)")

# --------------------------------------------------------------------------- #
# Label all 243 runes                                                          #
# --------------------------------------------------------------------------- #

all_runes = pd.DataFrame(
    list(itertools.product(SYMBOLS, repeat=5)),
    columns=POS,
)
all_runes['spell'] = model.predict(all_runes).astype(int)

spells = all_runes[all_runes['spell'] == 1][''.join(POS[i] for i in range(5))]
spells_list = [''.join(row) for row in all_runes[all_runes['spell'] == 1][POS].values]
print(f"\nAll 243 runes labeled: {all_runes['spell'].sum()} spells, "
      f"{(all_runes['spell'] == 0).sum()} non-spells")
print("Spell runes:", ' '.join(spells_list))

# --------------------------------------------------------------------------- #
# Distill into a shallow decision tree                                         #
# --------------------------------------------------------------------------- #
# OrdinalEncoder: F→0, W→1, E→2  (alphabetical)
# Splits read as: p <= 0.5 → F only | p <= 1.5 → F or W | p > 1.5 → E only

enc = OrdinalEncoder(categories=[SYMBOLS] * 5)
X_all = enc.fit_transform(all_runes[POS])
y_all = all_runes['spell'].values

print("\n--- Decision tree distillation ---")
for depth in range(1, 7):
    dt = DecisionTreeClassifier(max_depth=depth, random_state=0)
    dt.fit(X_all, y_all)
    acc = dt.score(X_all, y_all)
    print(f"  depth={depth}  accuracy={acc:.1%}", end='')
    if acc == 1.0:
        print("  ← perfect fit, rule found")
        break
    print()

print()
print("Encoding: F=0  W=1  E=2  →  'p <= 0.5' means F, 'p <= 1.5' means F or W, 'p > 1.5' means E")
print()
print(export_text(dt, feature_names=POS))

# --------------------------------------------------------------------------- #
# Write test predictions                                                       #
# --------------------------------------------------------------------------- #

X_test, test_runes = load_unlabeled('test_runes.csv')
y_test_pred = model.predict(X_test).astype(int)

out = pd.DataFrame({'rune': test_runes.values, 'spell': y_test_pred})
out.to_csv('answers-catboost.csv', index=False)
print(f"Predictions written to answers-catboost.csv")
