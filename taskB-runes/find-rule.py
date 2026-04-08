#!/usr/bin/env python3
"""Rule extraction for magic runes via MLP oracle.

Strategy:
  1. Train the 100%-accurate MLP (same setup as runes-kit.py).
  2. Label all 243 possible runes with it.
  3. Distill those ground-truth labels into the shallowest decision tree that fits
     perfectly → human-readable if-then rule.

Feature sets tried in order:
  - 5 positional (simplest)
  - 5 positional + 4 bigrams
  - 5 positional + 4 bigrams + 3 trigrams
"""

import itertools
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import OrdinalEncoder

from example.common import encode, load_labeled

SYMBOLS = ['F', 'W', 'E']
BIGRAMS  = [''.join(b) for b in itertools.product(SYMBOLS, repeat=2)]
TRIGRAMS = [''.join(t) for t in itertools.product(SYMBOLS, repeat=3)]


# --------------------------------------------------------------------------- #
# Train MLP oracle (identical to runes-kit.py)                                #
# --------------------------------------------------------------------------- #

def load_train(path):
    runes, labels = load_labeled(path)
    return np.array(runes), np.array(labels)

X_train, y_train = load_train('train_runes.csv')
n_spell = int(y_train.sum())
print(f"Training MLP on {len(y_train)} runes  ({n_spell} spells, {len(y_train) - n_spell} non-spells)")

mlp = MLPClassifier(
    hidden_layer_sizes=(15, 5),
    activation='relu',
    solver='adam',
    learning_rate_init=0.005,
    max_iter=5000,
    random_state=1,
    verbose=False,
)
mlp.fit(X_train, y_train)
print(f"MLP train accuracy: {mlp.score(X_train, y_train):.1%}")

# --------------------------------------------------------------------------- #
# Verify against answers.csv                                                   #
# --------------------------------------------------------------------------- #

X_ans, y_ans = load_train('answers.csv')
ans_acc = mlp.score(X_ans, y_ans)
print(f"MLP answers.csv accuracy: {ans_acc:.1%}  ({int((mlp.predict(X_ans) == y_ans).sum())}/{len(y_ans)} correct)")

# --------------------------------------------------------------------------- #
# Oracle: label all 243 runes                                                  #
# --------------------------------------------------------------------------- #

all_runes = [''.join(r) for r in itertools.product(SYMBOLS, repeat=5)]
X_all_51  = np.array([encode(r) for r in all_runes])
y_oracle  = mlp.predict(X_all_51).astype(int)

spells = [r for r, y in zip(all_runes, y_oracle) if y == 1]
print(f"\nOracle labels: {y_oracle.sum()} spells, {(y_oracle == 0).sum()} non-spells out of 243")
print("Spell runes:", ' '.join(spells))

# --------------------------------------------------------------------------- #
# Distillation feature sets                                                    #
# --------------------------------------------------------------------------- #

def pos_features(rune):
    return list(rune)

def pos_bi_features(rune):
    return list(rune) + [rune[i] + rune[i+1] for i in range(4)]

def pos_bi_tri_features(rune):
    return list(rune) + [rune[i] + rune[i+1] for i in range(4)] \
                      + [rune[i] + rune[i+1] + rune[i+2] for i in range(3)]

def count_features(rune):
    return [rune.count('F'), rune.count('W'), rune.count('E')]

SYM_ORD = {'F': 0, 'W': 1, 'E': 2}

def count_pos_features(rune):
    return count_features(rune) + [SYM_ORD[c] for c in rune]

# Pairwise equality: adjacent (01,12,23,34) + skip-1 (02,13,24) + skip-2 (03,14) + ends (04)
PAIR_NAMES = ['p0=p1', 'p1=p2', 'p2=p3', 'p3=p4',
              'p0=p2', 'p1=p3', 'p2=p4',
              'p0=p3', 'p1=p4',
              'p0=p4']
PAIR_IDX   = [(0,1),(1,2),(2,3),(3,4),
              (0,2),(1,3),(2,4),
              (0,3),(1,4),
              (0,4)]

def pair_features(rune):
    return [int(rune[i] == rune[j]) for i, j in PAIR_IDX]

def pair_pos_features(rune):
    return pair_features(rune) + [SYM_ORD[c] for c in rune]

BI_ORD = {b: i for i, b in enumerate(BIGRAMS)}  # 'EE'->0 .. 'WW'->8

def p13_features(rune):
    return [rune[1] + rune[3]]

def p13_pos_features(rune):
    return [BI_ORD[rune[1] + rune[3]]] + [SYM_ORD[c] for c in rune]

def p024_features(rune):
    return [rune[0] + rune[2] + rune[4]]

def p024_p13_features(rune):
    return [rune[0] + rune[2] + rune[4], rune[1] + rune[3]]

FEATURE_SETS = [
    ("p024 only",             p024_features,     [TRIGRAMS],           ['p024']),
    ("p13 only",              p13_features,      [BIGRAMS],            ['p13']),
    ("p024 + p13",            p024_p13_features, [TRIGRAMS, BIGRAMS],  ['p024', 'p13']),
    ("p13 + positional",      p13_pos_features,  None,                 ['p13'] + [f'p{i}' for i in range(5)]),
    ("positional only",       pos_features,      [SYMBOLS]*5,          [f'p{i}' for i in range(5)]),
]

# --------------------------------------------------------------------------- #
# Depth scan for each feature set                                              #
# --------------------------------------------------------------------------- #

for fs_name, fs_fn, fs_cats, fs_feat_names in FEATURE_SETS:
    print(f"\n=== Distillation: {fs_name} ===")
    X_fs = [fs_fn(r) for r in all_runes]
    if fs_cats is None:
        X_enc = np.array(X_fs, dtype=float)
    else:
        enc = OrdinalEncoder(categories=fs_cats)
        X_enc = enc.fit_transform(X_fs)

    best_dt = None
    for depth in range(1, 9):
        dt = DecisionTreeClassifier(max_depth=depth, random_state=0)
        dt.fit(X_enc, y_oracle)
        acc = dt.score(X_enc, y_oracle)
        print(f"  depth={depth}  accuracy={acc:.1%}", end='')
        if acc == 1.0:
            print("  <- perfect fit, rule found")
            best_dt = dt
            break
        print()

    if best_dt is not None:
        print()
        if fs_cats is not None:
            print("Encoding: F=0  W=1  E=2")
            print("  p <= 0.5  means  == F  |  p <= 1.5  means  in {F,W}  |  p > 1.5  means  == E")
        print()
        print(export_text(best_dt, feature_names=fs_feat_names))
    else:
        print(f"  -> no perfect fit within depth 8")
