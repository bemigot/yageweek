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
    """One-hot encode a 5-char rune -> 15-element vector."""
    vec = np.zeros(15)
    for i, ch in enumerate(rune):
        vec[i * 3 + SYMBOLS[ch]] = 1.0
    return vec

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
    X = np.array(runes).T            # (15, m)
    Y = np.array(labels).reshape(1, -1)  # (1, m)
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
    X = np.array(runes).T            # (15, m)
    return X, names

def train(X, Y, layers_dims, learning_rate=0.1, num_iterations=5000, print_every=500):
    np.random.seed(1)
    parameters = initialize_parameters_deep(layers_dims)

    for i in range(num_iterations):
        AL, caches = L_model_forward(X, parameters)
        cost = compute_cost(AL, Y)
        grads = L_model_backward(AL, Y, caches)
        parameters = update_parameters(parameters, grads, learning_rate)

        if print_every and (i % print_every == 0 or i == num_iterations - 1):
            print(f"  iter {i:5d}  cost {cost:.6f}")

    return parameters

def predict(X, parameters):
    AL, _ = L_model_forward(X, parameters)
    return (AL > 0.5).astype(int)


# --- main ---
X_train, Y_train = load_train('train_runes.csv')
X_test, test_names = load_test('test_runes.csv')

m = X_train.shape[1]
n_spell = int(Y_train.sum())
print(f"Training on {m} runes  ({n_spell} spells, {m - n_spell} non-spells)")

layers_dims = [15, 5, 1]
print(f"Architecture: {layers_dims}  lr=0.1  iters=5000")

parameters = train(X_train, Y_train, layers_dims)

train_preds = predict(X_train, parameters)
train_acc = float(np.mean(train_preds == Y_train))
print(f"Train accuracy: {train_acc:.1%}")

test_preds = predict(X_test, parameters)

with open('answers.csv', 'w') as f:
    f.write('rune,spell\n')
    for name, pred in zip(test_names, test_preds[0]):
        f.write(f'{name},{pred}\n')

print(f"Saved answers.csv  ({len(test_names)} predictions)")
