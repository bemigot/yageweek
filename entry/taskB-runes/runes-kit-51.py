#!/usr/bin/env python3
"""Rune spell detector - scikit-learn edition.

Architecture: [51 → 15 → 5 → 1]  (MLPClassifier, hidden_layer_sizes=(15, 5))
Features: 15 positional one-hot + 36 consecutive-bigram one-hot = 51 total
"""
import numpy as np
from sklearn.neural_network import MLPClassifier

from example.common import load_labeled, load_unlabeled

def load_train(path):
    runes, labels = load_labeled(path)
    return np.array(runes), np.array(labels)  # (m, 51), (m,)

def load_test(path):
    runes, names = load_unlabeled(path)
    return np.array(runes), names  # (m, 51)

# --- load data ---
X_train, y_train = load_train('train_runes.csv')
X_test, test_names = load_test('test_runes.csv')

m = len(y_train)
n_spell = int(y_train.sum())
print(f"Training on {m} runes  ({n_spell} spells, {m - n_spell} non-spells)")
print(f"Input features: {X_train.shape[1]}  (15 positional + 36 bigram)")

# --- build model matching [51 → 15 → 5 → 1] ---
clf = MLPClassifier(
    hidden_layer_sizes=(15, 5),
    activation='relu',
    solver='adam',
    learning_rate_init=0.005,
    max_iter=5000,
    random_state=1,
    verbose=False,
)
print(f"Architecture: [51 → 15 → 5 → 1]  (hidden_layer_sizes={clf.hidden_layer_sizes})")
print()

clf.fit(X_train, y_train)

train_acc = clf.score(X_train, y_train)
print(f"Train accuracy: {train_acc:.1%}")

# --- evaluate against answers.csv (read-only, never rewritten) ---
X_ans, ans_names = load_test('answers.csv')
y_ans_true = []
with open('answers.csv') as f:
    next(f)
    for line in f:
        line = line.strip()
        if not line:
            continue
        y_ans_true.append(int(line.split(',')[1]))
y_ans_true = np.array(y_ans_true)

y_ans_pred = clf.predict(X_ans)
ans_acc = np.mean(y_ans_pred == y_ans_true)
print(f"answers.csv accuracy: {ans_acc:.1%}  ({int((y_ans_pred == y_ans_true).sum())}/{len(y_ans_true)} correct)")

# --- predict on test_runes.csv ---
y_test_pred = clf.predict(X_test)
print(f"\nTest predictions (test_runes.csv):")
for name, pred in zip(test_names, y_test_pred):
    print(f"  {name}: {pred}")
