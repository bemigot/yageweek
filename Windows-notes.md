# Windows-notes

Gotchas observed while running data-science / ML workloads on urz-win
(i5-1135G7, Pixi-managed `iap` env, Python 3.14). Sibling to
[`python-env.md`](python-env.md) — that file is the live config recipe;
this file is the lessons-learned log behind it.

## Pixi vs Conda

- **conda-forge `mkl` drags in `llvm-openmp`** as a hard dep. MKL itself
  also bundles `libiomp5md.dll`. End result: two OpenMP runtimes loaded
  at once on every script start. `threadpoolctl.threadpool_info()`
  reports both (`libiomp` and `libomp`); `threadpoolctl` emits a
  RuntimeWarning about potential deadlocks.
  - **Confirmed**: this is a correctness concern (joblib docs), not a
    perf hit. We tested by building a parallel scratch env (`iapintel`)
    sourced from Intel's conda channel — single-OpenMP, no warning —
    and `runes.py` was actually *slower* there, not faster. Dual-OMP is
    not the cause of the iap-vs-idp wall-time gap.
- **Intel's win-64 channel
  (`https://software.repos.intel.com/python/conda`) lacks py314 builds
  as of 2026-05-08.** Latest is py313 for `numpy`, `scipy`,
  `scikit-learn-intelex`. Switching `iap` to Intel channel would force
  a Python 3.14 → 3.13 downgrade. Revisit when py314 ships.
- **Intel channel does help sklearn workloads** (~28% faster: 1.95s →
  1.41s on `runes-kit-36-5-1.py`), even beating Linux idp's 1.636s.
  Not enough on its own to justify the py314 downgrade today.
- **Pixi env activation modes** map to conda equivalents — see
  [python-env.md § Activation modes](python-env.md#activation-modes-analogs-of-conda-activate).
  Worth remembering: there is no `pixi deactivate`; close the shell or
  open a new one.
- **Pixi shell-hook on PowerShell:**
  `pixi shell-hook -e iap | Out-String | Invoke-Expression`. The
  `Out-String` step is required (raw object pipeline doesn't evaluate).

## MKL on Tiger Lake

- **Dispatch is AVX-512** (with DL Boost / VNNI), not SSE/AVX2. Confirm
  with `MKL_VERBOSE=1`:
  ```
  MKL_VERBOSE oneMKL ... Intel(R) Advanced Vector Extensions 512
  (Intel(R) AVX-512) with support of Intel(R) Deep Learning Boost
  ```
- **For tight Python loops with tiny matrices, `MKL_NUM_THREADS=1` is
  faster than default 4 threads.** On `runes.py` (30000 iters of
  15×170 / 51×170 matmuls): 5.07s → 4.73s wall, 13.95s → 4.45s user.
  Reason: MKL's per-call thread-dispatch overhead exceeds the
  per-matmul compute when matrices are small.
  - This trick is workload-specific. Don't bake it into env activation
    — set per-script when small-matmul tight loops are the hot path.

## Python startup / import cost on Windows

- **Windows preamble dominates short-lived scripts.** Empty `python -c
  pass` is ~25ms (cheap). But a typical "data-science script" preamble
  — `from sklearnex import patch_sklearn; patch_sklearn(); import
  numpy, sklearn, pandas` — runs ~1.5–2.0s on iap. Linux idp pays a
  fraction of this. So:
  - For scripts where actual algorithmic work is <1s (e.g. SVM with
    GridSearch on 170 rows: ~0.5s), external wall is 70-80% preamble.
  - Conclusions about "X is faster than Y" drawn from external `time`
    on Windows can be entirely preamble noise.
- **`patch_sklearn()` alone costs ~0.5s on Windows.** Adding it to one
  script and not another silently biases comparisons. We hit this with
  `runes-SVM.py` (commit `2fe8d1a` added the patch) vs `runes-kit.py`
  (had it from creation).

## Timing on Windows (no `time` command)

- **`Start-Process -PassThru -Wait` returns the *launcher* process,
  not the child.** Calling `pixi run -e iap python script.py` and
  reading `UserProcessorTime` measures pixi.exe — typically near zero
  while the actual Python child does seconds of work. Misleading.
- **Bypass pixi for accurate per-process timing.** Activate the env via
  `pixi shell-hook` once, then call `.pixi/envs/iap/python.exe` directly:
  ```powershell
  pixi shell-hook -e iap | Out-String | Invoke-Expression
  $proc = Start-Process -FilePath "C:\e\yageweek\.pixi\envs\iap\python.exe" `
      -ArgumentList @("script.py") -NoNewWindow -PassThru -Wait `
      -RedirectStandardOutput "$env:TEMP\out.txt"
  $real = ($proc.ExitTime - $proc.StartTime).TotalSeconds
  $user = $proc.UserProcessorTime.TotalSeconds
  ```
  This gives clean real/user numbers comparable to Linux `time`.
- **Direct `python.exe` invocation needs `Library\bin` on PATH** —
  otherwise `import numpy` fails with cryptic exit code (no stderr).
  The `pixi shell-hook` evaluation handles this.

## PowerShell pitfalls (PS 5.1)

- **`PYTHONUTF8 = "1"` is mandatory** in the iap env (set via
  `[tool.pixi.activation.env]` in pyproject.toml). Without it,
  Cyrillic/Unicode prints crash on Windows console code pages.
- **`Get-Content` defaults to system codepage**, not UTF-8.
  Captured stdout from a Python script that prints non-ASCII (Russian
  Время / Общее) will silently lose those lines unless you pass
  `-Encoding utf8`. Cost us 5 minutes chasing a "missing" timer line
  that was actually right there in the file.
- **Native `git.exe` chokes on PowerShell here-strings with embedded
  `"`.** PowerShell splits the string on the inner quotes and passes
  fragments as positional args; git interprets them as pathspecs.
  Workaround: write the message to a temp file and `git commit -F file`.
- **Never `2>&1` against a native exe.** PowerShell wraps each stderr
  line as a NativeCommandError ErrorRecord and may set `$?` to false
  even on exit code 0. Stderr is captured automatically; don't redirect.

## Measurement methodology gotchas

- **Internal script timers may exclude imports.** `runes-SVM.py`'s
  `Общее время скрипта` ("total script time") is misleading — its
  `start_total = time.time()` sits at line 159, *after* imports +
  `patch_sklearn` + `pd.read_csv` + feature engineering. Reading that
  number as "the script's runtime" hides ~2s of preamble.
- **Comparing internal-clock readings of script A against external
  `time` of script B is apples-to-oranges**, especially on Windows
  where preamble is heavy.
- **External wall on Windows is dominated by preamble for short
  scripts.** Even if algorithmic work is genuinely 2× faster (e.g. SVM
  vs minimal-net: ~0.5s vs ~1s), wall-clock can show the *opposite*
  ranking once both pay 1.5s+ of imports.

## Specific findings on iap (urz-win)

- **`runes.py` on iap (5.5s) vs idp (4.3s) — ~28% slower on Windows,
  cause not fully diagnosed.** Disproven hypotheses: dual-OpenMP
  (iapintel single-OMP was also slow), startup overhead (sub-100ms),
  pure NumPy compute (microbench identical), Defender real-time
  scanning of the env path (5×5 runs on 2026-05-08: real avg 5.549s
  baseline vs 5.660s with the env excluded — within per-run jitter,
  both ranges overlap). Remaining candidates: Windows fs/syscall
  latency, or some Python 3.14-vs-3.12 interpreter behavior on this
  specific bytecode.
  - Reproduce / revert the Defender exclusion (elevated PowerShell):
    ```powershell
    Add-MpPreference    -ExclusionPath 'C:\e\yageweek\.pixi\envs\iap'
    Remove-MpPreference -ExclusionPath 'C:\e\yageweek\.pixi\envs\iap'
    Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
    ```
- **`runes-kit-*.py` on iap is competitive with idp** for sklearn
  workloads. Differences are small and dominated by sklearn-internal
  changes between releases, not env tax.
- **threadpoolctl reports 3 thread pools on iap**: `mkl_rt` (4t),
  `libiomp5md` (4t), `libomp` (4t). The third (`libomp`) comes from
  conda-forge's `llvm-openmp` package pulled by `mkl`'s deps. It's
  loaded but not actively used by NumPy/sklearn — symptom, not the
  performance disease.

## Open threads

- **idp/Linux SVM measurement still pending.** Re-run `runes-SVM.py`
  (with current `patch_sklearn()`) on idp or pixi-pug to get a fair
  iap-vs-idp comparison on the SVM table.
- **`KMP_DUPLICATE_LIB_OK=TRUE` test.** Would silence the threadpoolctl
  warning without changing channels. Cosmetic only — won't change perf
  given dual-OMP isn't the actual perf cause.
