import numpy as np

SYMBOLS = {'F': 0, 'W': 1, 'E': 2}

def encode(rune):
    """One-hot encode positions (15) + consecutive bigrams (36) -> 51-element vector."""
    pos = np.zeros(15)
    for i, ch in enumerate(rune):
        pos[i * 3 + SYMBOLS[ch]] = 1.0
    bi = np.zeros(36)
    for i in range(4):
        a, b = SYMBOLS[rune[i]], SYMBOLS[rune[i + 1]]
        bi[i * 9 + a * 3 + b] = 1.0
    return np.concatenate([pos, bi])

def load_labeled(path):
    """Return (encoded vectors, int labels) as plain lists."""
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
    return runes, labels

def load_unlabeled(path):
    """Return (encoded vectors, rune names) as plain lists.
    Accepts rune-only lines as well as rune,label lines (label is ignored).
    """
    runes, names = [], []
    with open(path) as f:
        next(f)
        for line in f:
            line = line.strip()
            if not line:
                continue
            name = line.split(',')[0]
            runes.append(encode(name))
            names.append(name)
    return runes, names
