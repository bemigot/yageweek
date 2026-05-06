#!/usr/bin/env python3
import numpy as np

from example.common import load_labeled, load_unlabeled
from example.dnn_app_utils_v3 import (
    initialize_parameters_deep,
    L_model_forward,
    compute_cost,
    L_model_backward,
    update_parameters,
)

def load_train(path):
    runes, labels = load_labeled(path)
    return np.array(runes).T, np.array(labels).reshape(1, -1)  # (51, m), (1, m)

def load_test(path):
    runes, names = load_unlabeled(path)
    return np.array(runes).T, names  # (51, m)

def train(X, Y, layers_dims, seed, learning_rate, num_iterations, print_every=1000):
    parameters = initialize_parameters_deep(layers_dims, seed=seed)
    for i in range(num_iterations):
        AL, caches = L_model_forward(X, parameters)
        cost = compute_cost(AL, Y)
        grads = L_model_backward(AL, Y, caches)
        parameters = update_parameters(parameters, grads, learning_rate)
        if print_every and (i % print_every == 0 or i == num_iterations - 1):
            preds = (AL > 0.5).astype(int)
            acc = float(np.mean(preds == Y))
            print(f"  iter {i:5d}  cost {cost:.6f}  train_acc {acc:.1%}")
    return parameters

def predict_proba(X, parameters):
    AL, _ = L_model_forward(X, parameters)
    return AL


# --- main ---
X_train, Y_train = load_train('train_runes.csv')
X_test, test_names = load_test('test_runes.csv')

m = X_train.shape[1]
n_spell = int(Y_train.sum())
print(f"Training on {m} runes  ({n_spell} spells, {m - n_spell} non-spells) using NumPy {np.__version__}")
print(f"Input features: {X_train.shape[0]}  (15 positional + 36 bigram)")

layers_dims = [51, 15, 5, 1]
learning_rate = 0.005
num_iterations = 30000
seed = 1
print(f"Architecture: {layers_dims}  lr={learning_rate}  iters={num_iterations}  seed={seed}")
print()

parameters = train(X_train, Y_train, layers_dims, seed, learning_rate, num_iterations)

train_preds = (predict_proba(X_train, parameters) > 0.5).astype(int)
train_acc = float(np.mean(train_preds == Y_train))
print(f"\nFinal train accuracy: {train_acc:.1%}")

test_preds = (predict_proba(X_test, parameters) > 0.5).astype(int)

with open('answers.csv', 'w') as f:
    f.write('rune,spell\n')
    for name, pred in zip(test_names, test_preds[0]):
        f.write(f'{name},{pred}\n')

print(f"Saved answers.csv  ({len(test_names)} predictions)")
