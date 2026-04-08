#!/usr/bin/env python3
"""Rune spell detector — CatBoost edition.

Strategy:
  1. Train CatBoostClassifier on 170 labeled runes (raw F/W/E + trigrams, no encoding).
  2. Label all 243 possible runes.
  3. Distill into a shallow sklearn DecisionTree → human-readable rule.

Features: 5 positional + 3 trigram categorical columns (9 total).
Trigrams: p0p1p2, p1p2p3, p2p3p4 — 27 possible values each.
"""

import csv
import itertools
import numpy as np
from catboost import CatBoostClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OrdinalEncoder

SYMBOLS = ['F', 'W', 'E']
POS = [f'p{i}' for i in range(5)]
BI  = ['b01', 'b12', 'b23', 'b34']
ALL_FEATURES = POS + BI
N_CAT = len(ALL_FEATURES)

BIGRAMS = [''.join(b) for b in itertools.product(SYMBOLS, repeat=2)]  # 9 values


# --------------------------------------------------------------------------- #
# Feature construction                                                         #
# --------------------------------------------------------------------------- #

def make_features(rune: list[str]) -> list[str]:
    """5 positional + 4 bigram categorical features."""
    bi = [rune[i] + rune[i+1] for i in range(4)]
    return rune + bi


# --------------------------------------------------------------------------- #
# Data loading                                                                 #
# --------------------------------------------------------------------------- #

def load_labeled(path):
    """Return X (list of feature lists), y (list of ints)."""
    X, y = [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append(make_features(list(row['rune'])))
            y.append(int(row['spell']))
    return X, y


def load_unlabeled(path):
    """Return X (list of feature lists), rune strings."""
    X, names = [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append(make_features(list(row['rune'])))
            names.append(row['rune'])
    return X, names


# --------------------------------------------------------------------------- #
# Train                                                                        #
# --------------------------------------------------------------------------- #

X_train, y_train = load_labeled('train_runes.csv')
n_spell = sum(y_train)
print(f"Training on {len(y_train)} runes  ({n_spell} spells, {len(y_train) - n_spell} non-spells)")
print(f"Features: {ALL_FEATURES}")

model = CatBoostClassifier(
    iterations=2000,
    depth=3,
    learning_rate=0.05,
    cat_features=list(range(N_CAT)),
    verbose=False,
    random_seed=42,
)
model.fit(X_train, y_train)

y_train_pred = model.predict(X_train).astype(int)
train_acc = np.mean(y_train_pred == np.array(y_train))
print(f"Train accuracy: {train_acc:.1%}")

# --------------------------------------------------------------------------- #
# Evaluate against answers.csv                                                 #
# --------------------------------------------------------------------------- #

X_ans, ans_names = load_unlabeled('answers.csv')
_, y_ans_true = load_labeled('answers.csv')
y_ans_pred = model.predict(X_ans).astype(int)
y_ans_true = np.array(y_ans_true)
ans_acc = np.mean(y_ans_pred == y_ans_true)
print(f"answers.csv accuracy: {ans_acc:.1%}  ({(y_ans_pred == y_ans_true).sum()}/{len(y_ans_true)} correct)")
for name, pred, true in zip(ans_names, y_ans_pred, y_ans_true):
    if pred != true:
        print(f"  WRONG: {name}  predicted={pred}  truth={true}")

# --------------------------------------------------------------------------- #
# Label all 243 runes                                                          #
# --------------------------------------------------------------------------- #

all_runes = [list(r) for r in itertools.product(SYMBOLS, repeat=5)]
all_names = [''.join(r) for r in all_runes]
all_X = [make_features(r) for r in all_runes]
all_y = model.predict(all_X).astype(int)

spells = [name for name, pred in zip(all_names, all_y) if pred == 1]
print(f"\nAll 243 runes labeled: {all_y.sum()} spells, {(all_y == 0).sum()} non-spells")
print("Spell runes:", ' '.join(spells))

# --------------------------------------------------------------------------- #
# Distill into a shallow decision tree                                         #
# --------------------------------------------------------------------------- #
# Positional encoding: F→0, W→1, E→2
# Trigram encoding: alphabetical order over 27 combinations
# Split thresholds are less readable for trigrams; feature names make it clear.

pos_cats = [SYMBOLS] * 5
bi_cats  = [BIGRAMS] * 4
enc = OrdinalEncoder(categories=pos_cats + bi_cats)
X_enc = enc.fit_transform(all_X)

print("\n--- Decision tree distillation ---")
dt = None
for depth in range(1, 9):
    dt = DecisionTreeClassifier(max_depth=depth, random_state=0)
    dt.fit(X_enc, all_y)
    acc = dt.score(X_enc, all_y)
    print(f"  depth={depth}  accuracy={acc:.1%}", end='')
    if acc == 1.0:
        print("  <- perfect fit, rule found")
        break
    print()

print()
print("Positional encoding: F=0  W=1  E=2")
print("  p <= 0.5  means  p == F")
print("  p <= 1.5  means  p in {F, W}")
print("  p >  1.5  means  p == E")
print("Bigram encoding: alphabetical over 9 values (EE=0 … WW=8)")
print()
print(export_text(dt, feature_names=ALL_FEATURES))

# --------------------------------------------------------------------------- #
# Write test predictions                                                       #
# --------------------------------------------------------------------------- #

X_test, test_names = load_unlabeled('test_runes.csv')
y_test_pred = model.predict(X_test).astype(int)

with open('answers-catboost.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['rune', 'spell'])
    for name, pred in zip(test_names, y_test_pred):
        writer.writerow([name, pred])

print(f"Predictions written to answers-catboost.csv")
