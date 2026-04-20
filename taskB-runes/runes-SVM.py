#!/usr/bin/env python3
# coding: utf-8

# Originally:
# https://github.com/EvgeniyKorovin1/AgentsWeek-TaskSolutions/blob/1974a63162cd9884a794b236c9f529c3e2b58d9e/Tasks/Task_02/Solution_WithExplanation.ipynb

# **Магические руны Элдории**
# В этой задаче нужно определить, какие 5-символьные последовательности из символов `F`, `W` и `E` являются валидными заклинаниями.
# 
# На первый взгляд задача выглядит простой:
# - алфавит маленький;
# - длина строки фиксирована;
# - объектов немного.
# 
# Но именно такие задачи часто оказываются нетривиальными:  
# модель должна не просто “видеть буквы”, а уловить скрытые закономерности между их позициями и сочетаниями.
# 
# **Почему эта задача вызвала споры**
# 
# Во время разбора задачи у участников возникли два лагеря:
# - одни использовали бустинги и получали примерно 95–97 баллов;
# - другие писали, что SVM даёт 100 баллов.
# 
# Это хороший пример того, что не существует “всемогущей” модели, которая всегда лучше остальных.
# Для маленькой дискретной задачи с короткими строками и хорошо сконструированными признаками метод опорных векторов может оказаться сильнее популярных ансамблей деревьев.
# 
# ## **Общая идея признаков**
# 
# Строка длины 5 сама по себе неудобна для классических моделей машинного обучения, поэтому её нужно превратить в числовое описание.
# 
# Здесь используются три группы признаков:
# 
# 1. **Позиционные one-hot признаки**  
#    Для каждой позиции учитывается, какой символ в ней стоит.
# 
# 2. **Попарные взаимодействия между позициями**  
#    Важны не только отдельные символы, но и их комбинации в разных местах строки.
# 
# 3. **Счётчики символов**  
#    Сколько раз в строке встретились `F`, `W` и `E`.
# 
# Такое представление уже позволяет классическим моделям видеть не просто строку, а её структурные свойства.
import os
import time
import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score


TRAIN_PATH = "train_runes.csv"
TEST_PATH = "test_runes.csv"
OUTPUT_PATH = "my_answers.csv"
REFERENCE_PATH = "answers.csv"

train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

print("Train shape:", train_df.shape)
print("Test shape :", test_df.shape)

train_df.head()


# ## Подготовка признаков
# вспомогательные функции, которые превращают строки с рунами в числовое представление.
def split_runes(series: pd.Series) -> pd.DataFrame:
    arr = series.astype(str).apply(list).tolist()
    return pd.DataFrame(arr, columns=[f"pos_{i}" for i in range(5)])


def make_ohe():
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


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


def evaluate_with_reference(pred_df: pd.DataFrame, reference_path: str):
    if not os.path.exists(reference_path):
        print(f"\nЭталонный файл не найден: {reference_path}")
        return

    ref_df = pd.read_csv(reference_path)

    if not {"rune", "spell"}.issubset(ref_df.columns):
        print("\nВ эталонном файле должны быть колонки: rune, spell")
        return

    merged = pred_df.merge(ref_df, on="rune", suffixes=("_pred", "_true"))

    if len(merged) != len(pred_df):
        print("\nWARN: не все руны совпали между prediction и reference.")

    y_pred = merged["spell_pred"].astype(int).to_numpy()
    y_true = merged["spell_true"].astype(int).to_numpy()

    hits = int((y_pred == y_true).sum())
    total = len(merged)
    acc = accuracy_score(y_true, y_pred)

    print("\n=== Автопроверка по эталону ===")
    print(f"Попаданий: {hits}/{total}")
    print(f"Accuracy : {acc:.6f}")

    errors = merged[merged["spell_pred"] != merged["spell_true"]].copy()
    if len(errors) == 0:
        print("Ошибок нет.")
    else:
        print("\nОшибочные руны:")
        print(errors[["rune", "spell_pred", "spell_true"]].to_string(index=False))


X_train, encoder = build_features_fit(train_df["rune"])
X_test = build_features_transform(test_df["rune"], encoder)
y = train_df["spell"].astype(int).to_numpy()

print("Shape train:", X_train.shape)
print("Shape test :", X_test.shape)

# Подход 2. SVM с подбором гиперпараметров
# Второй вариант - использовать метод опорных векторов и подобрать его параметры с помощью `GridSearchCV`.
# На практике именно этот подход оказался особенно сильным для данной задачи.
# 
# Почему это может происходить:
# - признаков немного;
# - структура признаков аккуратная и компактная;
# - задача напоминает классификацию в хорошо определённом признаковом пространстве;
# - SVM хорошо работает на небольших и средних датасетах с чёткой границей разделения.
# 
# Здесь мы перебираем 20 кандидатов:
# - 4 варианта для линейного ядра;
# - 16 вариантов для RBF-ядра.

start_total = time.time()

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


# ## Почему поиск делается без `probability=True`
# Во время перебора параметров важно не тратить лишнее время.
# Опция `probability=True` у `SVC` делает обучение заметно тяжелее,
# потому что дополнительно оцениваются вероятности.
# Поэтому в `GridSearchCV` удобнее сначала искать лучшие параметры без вероятностей,
# а уже после этого обучить финальную модель с теми же параметрами, но с `probability=True`.

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

print(f"Время финального fit: {end_final - start_final:.3f} сек")

test_proba = svm_final.predict_proba(X_test)[:, 1]
test_pred_svm = (test_proba >= 0.5).astype(int)

submission_svm = pd.DataFrame({
    "rune": test_df["rune"],
    "spell": test_pred_svm
})

submission_svm.to_csv(OUTPUT_PATH, index=False)

##print(f"Файл сохранён: {OUTPUT_PATH}")
#submission_svm.head(10)

#debug_df = pd.DataFrame({
#    "rune": test_df["rune"],
#    "proba_1": test_proba,
#    "pred": test_pred_svm,
#    "uncertainty": np.abs(test_proba - 0.5)
#}).sort_values("uncertainty", ascending=True)
#print("Топ-10 самых неуверенных предсказаний SVM:")
#print(debug_df.head(10).to_string(index=False))

#evaluate_with_reference(submission_svm, REFERENCE_PATH)
print(f"\nОбщее время скрипта: {time.time() - start_total:.3f} сек")


# SVM
# Плюсы:
# - для этой задачи может давать идеальный результат;
# - хорошо работает на компактных и информативных признаках;
# - подбор параметров оказывается достаточно недорогим.
# 
# Минусы:
# - требует более аккуратной настройки;
# - нужно понимать влияние ядра, `C` и `gamma`.

# ## Итоговый вывод
# 
# Эта задача интересна тем, что опровергает стереотип:
# > современные ансамбли деревьев лучше классических методов.
# 
# На структурированных коротких строках с хорошими признаками SVM
# показывает отличный результат и может выиграть у “модных” подходов.
