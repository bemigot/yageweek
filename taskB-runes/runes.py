#!/usr/bin/env python3
import numpy as np

from example.dnn_app_utils_v3 import (
    initialize_parameters_deep,
    L_model_forward,
    compute_cost,
    L_model_backward,
    update_parameters,
)

SYMBOLS = {'F': 0, 'W': 1, 'E': 2}

def encode(rune):
    """One-hot encode positions (15) + consecutive bigrams (36) -> 51-element vector."""
    # 15: individual positions
    pos = np.zeros(15)
    for i, ch in enumerate(rune):
        pos[i * 3 + SYMBOLS[ch]] = 1.0
    # 36: consecutive pairs at positions (0,1),(1,2),(2,3),(3,4)
    bi = np.zeros(36)
    for i in range(4):
        a, b = SYMBOLS[rune[i]], SYMBOLS[rune[i + 1]]
        bi[i * 9 + a * 3 + b] = 1.0
    return np.concatenate([pos, bi])

def load_train(path):
    runes, labels = [], []
    with open(path) as f:
        next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue
            rune, label = line.split(',')
            runes.append(encode(rune))
            labels.append(int(label))
    X = np.array(runes).T            # (51, m)
    Y = np.array(labels).reshape(1, -1)
    return X, Y

def load_test(path):
    runes, names = [], []
    with open(path) as f:
        next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue
            runes.append(encode(line))
            names.append(line)
    X = np.array(runes).T            # (51, m)
    return X, names

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
print(f"Training on {m} runes  ({n_spell} spells, {m - n_spell} non-spells)")
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
