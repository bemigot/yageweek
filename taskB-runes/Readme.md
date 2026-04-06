# Magic runes

In this task "rune" is a sequence of symbols:
- Runes use 3 symbols only: F (fire), W (water), E (Earth)
- All runes are 5 symbols long
- Some runes are magical - the task is to build a device for detecting those

**Dataset**: train_runes.csv, test_runes.csv:
- train_runes.csv - tagged dataset - column `spell` - 1 - true spell (79 runes), 0 - no magic (91 rune).
- test_runes.csv - untagged, your task is to predict the correct tag (0/1).

**Output** answers.csv - test_runes + predictions (column `spell`, where 1 - valid spell)

## Try 1+2 layer net - 3 false-negatives
- Input: one-hot encode each position → 15 input neurons (5 positions × 3 symbols)
- Architecture: `[15 → 5 → 1]` — fully connected hidden layer with ReLU, sigmoid output; bump hidden neurons if accuracy is low
- Train on all 170 labeled runes (no internal split) — dataset is too small to waste samples on validation, and test_runes.csv is the real target
- use only NumPy
- use [`example/deep.py`](example/deep.py) and [`example/dnn_app_utils_v3.py`](example/dnn_app_utils_v3.py) ideas

## Try 2: 1+3 layer net
- Input: one-hot encode each position (15) + 36 bigrams
- Architecture [51, 15, 5, 1]
- 20x smaller Learning Rate, 6x more iterations
- on 73-samples test_set: 3 negatives (0 - no-spell) -> 3 positives - 100% success
- [`runes-kit`](runes-kit.py) - same net, using `scikit-learn`

| Env                                                                        | Time real/user    |
|----------------------------------------------------------------------------|-------------------|
| Ryzen 5 3600 3.6-4.2 GHz / Python 3.12 - NumPy 1.26 (Ubuntu 24.04 default) | 11,417s / 11,388s |
| Ryzen 5 3600 3.6-4.2 GHz /                Python 3.12 - NumPy 2.4.4 (PyPi) |  4,750s /  5,539s |
| i5-1135G7 2.4-4.2 GHz / --------------- / Python 3.12 - NumPy 2.4.4 (PyPi) |  3.196s /  3.492s |
| i5-1135G7 2.4-4.2 GHz / Iris Xe 1.3 GHz / Python 3.12 - NumPy 2.3.2  [idp] |  4.309s / 15.676s |
| i5-1135G7 2.4-4.2 GHz / Iris Xe 1.3 GHz / Python 3.12 - scikit-learn [idp] |  2.054s /  2.152s |

[idp](https://www.intel.com/content/www/us/en/developer/articles/technical/get-started-with-intel-distribution-for-python.html)
```
which python  # ~/.conda/envs/idp/bin/python
python -V     # Python 3.12.12

numpy                        2.3.2    https://software.repos.intel.com/python/conda
scikit-learn                 1.8.0    conda-forge
scikit-learn-intelex         2025.9.0 https://software.repos.intel.com/python/conda
scipy                        1.16.3   https://software.repos.intel.com/python/conda
```
