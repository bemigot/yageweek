# Magic runes

In this task "rune" is a sequence of symbols:
- Runes use 3 symbols only: F (fire), W (water), E (Earth)
- All runes are 5 symbols long
- Some runes are magical - the task is to build a device for detecting those

**Dataset**: train_runes.csv, test_runes.csv:
- train_runes.csv - tagged dataset - column `spell` - 1 - true spell (79 runes), 0 - no magic (91 rune).
- test_runes.csv - untagged, you task is to predict the correct tag (0/1).

**Output** answers.csv - test_runes + predictions (column `spell`, where 1 - valid spell)

## Try 1+2 layer net
- Input: one-hot encode each position → 15 input neurons (5 positions × 3 symbols)
- Architecture: `[15 → 5 → 1]` — fully connected hidden layer with ReLU, sigmoid output; bump hidden neurons if accuracy is low
- Train on all 170 labeled runes (no internal split) — dataset is too small to waste samples on validation, and test_runes.csv is the real target
- use only NumPy - for running on my Iris Xe notebook ( `conda activate idp` -  Python 3.12 / numpy 2.2 / matplotlib 3.10)
- use [`example/deep.py`](example/deep.py) and [`example/dnn_app_utils_v3.py`](example/dnn_app_utils_v3.py) ideas

## Try 2: 1+3 layer net
- Input: one-hot encode each position (15) + 36 bigrams
- Architecture [51, 15, 5, 1]
- 20x smaller Learning Rate, 6x more iterations
- on 73-samples test_set: 3 negatives (0 - no-spell) -> 3 postives - 100% success
