#!/usr/bin/env python3
# coding: utf-8

"""
Originally:
https://github.com/EvgeniyKorovin1/AgentsWeek-TaskSolutions/blob/1974a63162cd9884a794b236c9f529c3e2b58d9e/Tasks/Task_02/Solution_WithExplanation.ipynb
"""
import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

TRAIN_PATH = "train_runes.csv"
TEST_PATH = "test_runes.csv"
OUTPUT_PATH = "my_answers.csv"
REFERENCE_PATH = "answers.csv"

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)
print("Shape train:", train_df.shape)
print("Shape test :", test_df.shape)

def split_runes(series: pd.Series) -> pd.DataFrame:
    arr = series.astype(str).apply(list).tolist()
    return pd.DataFrame(arr, columns=[f"pos_{i}" for i in range(5)])


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)


def build_count_features(pos_df: pd.DataFrame) -> np.ndarray:
    count_w = (pos_df == "W").sum(axis=1).to_numpy().reshape(-1, 1)
    count_f = (pos_df == "F").sum(axis=1).to_numpy().reshape(-1, 1)
    count_e = (pos_df == "E").sum(axis=1).to_numpy().reshape(-1, 1)
    return np.hstack([count_w, count_f, count_e]).astype(np.float32)


def build_pairwise_interactions(X_ohe: np.ndarray) -> np.ndarray:
    groups = [
        [0, 1, 2],      # pos_0
        [3, 4, 5],      # pos_1
        [6, 7, 8],      # pos_2
        [9, 10, 11],    # pos_3
        [12, 13, 14],   # pos_4
    ]

    features = []

    for i in range(5):
        for j in range(i + 1, 5):
            for c1 in groups[i]:
                for c2 in groups[j]:
                    col = (X_ohe[:, c1] * X_ohe[:, c2]).reshape(-1, 1)
                    features.append(col)

    return np.hstack(features).astype(np.float32)


def build_features_fit(runes: pd.Series):
    pos_df = split_runes(runes)

    encoder = make_ohe()
    X_ohe = encoder.fit_transform(pos_df).astype(np.float32)

    X_pair = build_pairwise_interactions(X_ohe)
    X_count = build_count_features(pos_df)

    X = np.hstack([X_ohe, X_pair, X_count]).astype(np.float32)
    return X, encoder


def build_features_transform(runes: pd.Series, encoder):
    pos_df = split_runes(runes)

    X_ohe = encoder.transform(pos_df).astype(np.float32)
    X_pair = build_pairwise_interactions(X_ohe)
    X_count = build_count_features(pos_df)

    X = np.hstack([X_ohe, X_pair, X_count]).astype(np.float32)
    return X


X_train, encoder = build_features_fit(train_df["rune"])
X_test = build_features_transform(test_df["rune"], encoder)
y = train_df["spell"].astype(int).to_numpy()

'''
Подход 2. SVM с подбором гиперпараметров

этот подход оказался особенно сильным для данной задачи.
Почему это может происходить:
- признаков немного;
- структура признаков аккуратная и компактная;
- задача напоминает классификацию в хорошо определённом признаковом пространстве;
- SVM хорошо работает на небольших и средних датасетах с чёткой границей разделения.

Здесь мы перебираем 20 кандидатов:
- 4 варианта для линейного ядра;
- 16 вариантов для RBF-ядра.
'''

start_ann = time.time()

svm_search = Pipeline([
    ("scaler", StandardScaler()),
    ("svc", SVC(
        random_state=42,
        probability=False,
        cache_size=1000
    ))
])

param_grid = [
    {
        "svc__kernel": ["linear"],
        "svc__C": [0.1, 1, 10, 100]
    },
    {
        "svc__kernel": ["rbf"],
        "svc__C": [0.1, 1, 10, 100],
        "svc__gamma": ["scale", 0.01, 0.1, 1]
    }
]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

grid = GridSearchCV(
    estimator=svm_search,
    param_grid=param_grid,
    scoring="accuracy",
    cv=cv,
    n_jobs=-1,
    refit=True,
    verbose=1
)

from joblib import parallel_backend
start_search = time.time()
with parallel_backend("threading"):
    grid.fit(X_train, y)
end_search = time.time()

print("\n=== Результат GridSearch ===")
print("Best params :", grid.best_params_)
print("Best CV acc :", grid.best_score_)
print(f"Время поиска: {end_search - start_search:.3f} сек")

'''
## Почему поиск делается без `probability=True`

Опция `probability=True` у `SVC` делает обучение заметно тяжелее,
потому что дополнительно оцениваются вероятности.
Поэтому в `GridSearchCV` сначала ищем лучшие параметры без вероятностей,
а после - обучаем финальную модель с теми же параметрами, но с `probability=True`.
'''

best_params = grid.best_params_
best_kernel = best_params["svc__kernel"]
best_c = best_params["svc__C"]
best_gamma = best_params.get("svc__gamma", "scale")

svm_final = Pipeline([
    ("scaler", StandardScaler()),
    ("svc", SVC(
        kernel=best_kernel,
        C=best_c,
        gamma=best_gamma,
        probability=True,
        random_state=42,
        cache_size=1000
    ))
])

start_final = time.time()
svm_final.fit(X_train, y)
end_final = time.time()

print(f"Final fit: {end_final - start_final:.3f} сек")

test_proba = svm_final.predict_proba(X_test)[:, 1]
test_pred_svm = (test_proba >= 0.5).astype(int)

submission_svm = pd.DataFrame({
    "rune": test_df["rune"],
    "spell": test_pred_svm
})

submission_svm.to_csv(OUTPUT_PATH, index=False)
print(f"\nAll dome: {time.time() - start_ann:.3f} сек")

debug_df = pd.DataFrame({
    "rune": test_df["rune"],
    "proba_1": test_proba,
    "pred": test_pred_svm,
    "uncertainty": np.abs(test_proba - 0.5)
}).sort_values("uncertainty", ascending=True)
print("Топ-10 самых неуверенных предсказаний SVM:")
print(debug_df.head(10).to_string(index=False))

'''
SVM
Плюсы:
- может дать 100% результат;
- хорошо работает на компактных и информативных признаках;
- подбор параметров оказывается недорогим.

Минусы:
- требует аккуратной настройки;
- нужно понимать влияние ядра, `C` и `gamma`.

## Выводы
На структурированных коротких строках с хорошими признаками SVM
показывает отличный результат и может выиграть у “модных” подходов.
'''
