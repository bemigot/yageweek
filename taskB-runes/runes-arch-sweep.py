#!/usr/bin/env python3
"""Architecture sweep: find the minimal MLP that achieves 100% on answers.csv.

Vary two axes independently:
  - Input features: positional-only (15), bigrams-only (36), both (51)
  - Hidden layers: none (linear), single layer, two layers

All runs use the same solver/lr/seed as runes-kit.py.
"""
try:
    from sklearnex import patch_sklearn
    patch_sklearn()
except ImportError:
    pass

import csv
import itertools
import numpy as np
from sklearn.neural_network import MLPClassifier

from example.common import encode

SYMBOLS = ['F', 'W', 'E']

# --------------------------------------------------------------------------- #
# Feature encoders                                                             #
# --------------------------------------------------------------------------- #

def enc_full(rune: str) -> np.ndarray:
    """51-dim: 15 positional one-hot + 36 bigram one-hot."""
    return encode(rune)

def enc_pos(rune: str) -> np.ndarray:
    """15-dim: positional one-hot only."""
    return encode(rune)[:15]

def enc_bi(rune: str) -> np.ndarray:
    """36-dim: bigram one-hot only."""
    return encode(rune)[15:]

# --------------------------------------------------------------------------- #
# Data loading                                                                 #
# --------------------------------------------------------------------------- #

def load(path, encoder):
    X, y, names = [], [], []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rune = row['rune']
            X.append(encoder(rune))
            names.append(rune)
            if 'spell' in row:
                y.append(int(row['spell']))
    return np.array(X), np.array(y) if y else None, names

# --------------------------------------------------------------------------- #
# Sweep definition                                                             #
# --------------------------------------------------------------------------- #

SWEEPS = [
    # (label,               encoder,  hidden_layer_sizes)
    ("[51→15→5→1] baseline", enc_full, (15, 5)),
    ("[51→5→1]",             enc_full, (5,)),
    ("[51→1]  linear",       enc_full, ()),
    ("[36→5→1]  bi only",    enc_bi,   (5,)),
    ("[36→1]  bi linear",    enc_bi,   ()),
    ("[15→36→1]  wide",      enc_pos,  (36,)),
    ("[15→15→1]",            enc_pos,  (15,)),
    ("[15→5→1]  Try1",       enc_pos,  (5,)),
]

MLP_KWARGS = dict(
    activation='relu',
    solver='adam',
    learning_rate_init=0.005,
    max_iter=5000,
    random_state=1,
    verbose=False,
)

# --------------------------------------------------------------------------- #
# Run sweep                                                                    #
# --------------------------------------------------------------------------- #

print(f"{'Architecture':<28}  {'train':>6}  {'ans.csv':>7}  {'correct':>9}")
print("-" * 58)

for label, encoder, hidden in SWEEPS:
    X_train, y_train, _ = load('train_runes.csv', encoder)
    X_ans,   y_ans,   _ = load('answers.csv',     encoder)

    clf = MLPClassifier(hidden_layer_sizes=hidden, **MLP_KWARGS)
    clf.fit(X_train, y_train)

    train_acc = clf.score(X_train, y_train)
    ans_acc   = clf.score(X_ans, y_ans)
    n_correct = int((clf.predict(X_ans) == y_ans).sum())

    flag = "  <-- 100%" if ans_acc == 1.0 else ""
    print(f"{label:<28}  {train_acc:>6.1%}  {ans_acc:>7.1%}  {n_correct:>4}/{len(y_ans)}{flag}")
