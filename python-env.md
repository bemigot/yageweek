# Python environments

A memo on managing Python environments on
**Linux** and **Windows 11** machines. **TODO** macOS on Apple Silicon.

## uv-first

a word on `pyproject.toml`
- [PEP 518 -- File specification](https://www.python.org/dev/peps/pep-0518/#specification) - since May 2016
- Python 3.11 introduced native TOML support - Oct. 2022
- https://github.com/carlosperate/awesome-pyproject

**Why not pip?**

1. No transactional installs. A conflict discovered late leaves `site-packages/`
   partially mutated; `pip install -U` exits 0 on a silently broken
   environment. No rollback.
2. No clean uninstall — `pip uninstall` only removes the top-level package;
   transitive deps stay behind as orphans. No native lockfile.
3. PEP 668 killed `--user` installs on Debian/Ubuntu.
   `--break-system-packages` is an ugly "remedy".

[`uv`](https://github.com/astral-sh/uv) replaces `pip`, `pip-tools`,
`pipx`, `virtualenv`, `venv`, and `pyenv`:
install Python interpreters, CLI tools, create venvs, resolve/lock/sync deps.
And as a rule it's noticeably faster than any of them.

*Reproducibility* through three checked-in files: `pyproject.toml` + `uv.lock` +
`.python-version`. `uv sync` on any host (or OS — see [cross-platform notes](#cross-platform-reach)
below) recreates the exact env. The lockfile encodes per-platform markers,
so the same lockfile works on Linux, macOS, and Windows.

Managed Python installs live under `~/.local/share/uv/python/` — self-contained,
never touches `/usr/bin/python3`. Patch upgrades auto-follow via minor-line
symlinks (install `3.14`, get `3.14.4` today and `3.14.5` tomorrow with
`uv python upgrade 3.14`). Uninstall is `rm -rf` on the uv data dir and the
binary at `~/.local/bin/uv` — no apt involvement, no residue.

Conda stays only where it earns its keep: urz's Intel-optimized numerics /
SYCL stack on Iris Xe (see [urz](#urz-conda--intel-channel) section).

### **pixi** - ongoing experiment

[Pixi](https://pixi.prefix.dev/latest/concepts/conda_pypi/) can replace both
`uv` and `conda`. See [urz-Windows story below](#urz-windows-pixi).
Same conda-forge ecosystem plus a PyPI bridge, single Rust binary,
single lockfile. See also
- Modular's recommendation on [pixi](https://docs.modular.com/pixi/)
- [Switching from conda to pixi - incl. *why*](https://x-zang.github.io/blog/switch-from-conda-to-pixi/)
- [another *why* - physics.Purdue.edu](https://analysis-facility.physics.purdue.edu/en/latest/guide-conda-to-pixi.html#why-migrate-to-pixi)
- [Migrate a conda project to pixi](https://pydevtools.com/handbook/tutorial/migrate-a-conda-project-to-pixi/) -
  [Tim Hopper, AI research engineer, Spotify](https://github.com/tdhopper)
- [2025-12-22 Anaconda - Conda + Pixi Quick Start](https://www.anaconda.com/blog/conda-pixi-quick-start-guide-python-environment-management)
- [2024-03-01 7 Reasons to Switch from Conda to Pixi](https://prefix.dev/blog/pixi_a_fast_conda_alternative)
- [2024-02-20 Adopting uv in pixi](https://prefix.dev/blog/uv_in_pixi)

## Python projects

Notable Python projects across the author's fleet. "Pin" is `.python-version`;
"Floor" is `requires-python` in `pyproject.toml`.

| Project | Host | Git | Pin / Floor | Key deps | Notes |
|---|---|---|---|---|---|
| `~/e/git-log-analysis` | pug | `gitlab.exactpro.com:mark.zhitomirski/git-log-analysis` | — / `>=3.12` | `gitpython` | No pin; venv rides the rolling `cpython-3.14` alias |
| `~/i/QM1` | pug | — (local) | `3.14` / `>=3.14` | `segno` | Pkg name `qr-maker`; tight pin and floor |
| `~/i/pnc.2` | pug | `github.com:bemigot/pnc.2` | `3.14` / `>=3.10` | `python-dotenv`, `python-telegram-bot>21` | Telegram bot; floor left low for reuse |
| `~/k/krisp-2025` | pug | `github.com:panzim/kb` | `3.13` / — | uv workspace (members: `backend`, `frontend`) | Pkg name `Panzim` |
| `~/p/let-a-tin` | urz | `github.com:bemigot/let-a-tin` (fork of `github.com:Trim/acme-dns-tiny`) | `3.14` / `>=3.12` | `python-dotenv` + stdlib | ACME DNS-01 client. Local branch `t0`. |
| `~/k/a1py` | urz | `github.com:mz0/a1py` | `3.14` / `>=3.13` | `fastapi`, `uvicorn`, `httpx`, `itsdangerous`, `python-dotenv` | FastAPI sandbox. |
| `C:\e\yageweek` | wig | — (local) | `3.14` / `>=3.14` | `numpy`, `scipy`, `scikit-learn`, `scikit-learn-intelex`, `pandas`, `joblib`, `mkl`, `matplotlib`, `plotly`, `catboost`, `jupyter` | AgentsWeek task solutions; (see [urz-Windows](#urz-windows-pixi)). |

## Fleet

| Host | Role | Arch / OS | Kernel | System `python3` | uv |
|---|---|---|---|---|---|
| `pug` | Desktop dev box          | x86_64 / Ubuntu 24.04 noble | 6.17 | 3.12 | 0.11.7 |
| `urz` | Laptop, 1135G7 (Linux)   | x86_64 / Ubuntu 24.04 noble | 6.17 | 3.12 | 0.11.7 |
| `wig` | Laptop, 1135G7 (Windows) | x86_64 / Windows 11 Pro | NT 10.0.26200 | — | — (Pixi) |

Per-host assessment:

- **`pug`** — primary workstation. `uv` at `~/.local/bin/uv`.
- **`urz`** — system-wide conda at `/opt/conda` (root-owned, base read-only) retained only for Intel-optimized numerics / SYCL on Iris Xe.
  Deep-dive in [urz: conda + Intel channel](#urz-conda--intel-channel) below.
- **`wig`** — same laptop, Windows 11 boot. **Pixi** unifying aproach tryout.
  Deep-dive in [urz-Windows: Pixi](#urz-windows-pixi) below.

Parity rules across the fleet:

- **Reproducible across hosts**: `pyproject.toml`, `uv.lock`, `.python-version`. Check these in; `uv sync` on another host rebuilds the rest.
- **Not reproducible**: `.venv/`, `~/.local/share/uv/python/`. Never copy these between hosts — symlinks bake in absolute paths.
- `uv self update` per host independently; pin uv in CI via `astral-sh/setup-uv` if reproducibility matters there.

### Bootstrapping uv on a new host

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # writes ~/.local/bin/uv
# Installer adds ~/.local/bin to PATH via ~/.bashrc.
```

For non-interactive SSH (e.g. `ssh <host> <cmd>` with `BatchMode=yes`),
`.bashrc` is skipped — export PATH explicitly:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Tooling baseline

| Tool | Where | Notes |
|---|---|---|
| `uv` | `~/.local/bin/uv` | 0.11.7 on `pug` and `urz` (2026-04-21). |
| System `python3` | `/usr/bin/python3` | 3.12.3 on Ubuntu 24.04 boxes. Don't pip into it. |
| uv-managed Pythons | `~/.local/share/uv/python/cpython-X.Y.Z-linux-<arch>-gnu/` | Installed lazily by `uv sync` / `uv python install` |
| Conda (`urz`) | `/opt/conda` | System-wide, root-owned, `base` is read-only — see "urz" section below |
| Pixi (`wig`) | `%USERPROFILE%\.pixi\bin\pixi.exe` | Installed via `winget install prefix-dev.pixi` |

Upgrade uv itself: [`uv self update`](https://docs.astral.sh/uv/reference/cli/#uv-self-update) (binary self-update; no apt involvement).

### Cross-platform reach

uv is a single Rust binary with first-party support across all three major
desktop OSes:

| OS | Architectures | Install |
|---|---|---|
| Linux | x86_64, aarch64, armv7 (glibc + musl variants) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| macOS | x86_64 (Intel), arm64 (Apple Silicon) | same installer, or `brew install uv` |
| Windows | x86_64, arm64 | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"`, or `winget install astral-sh.uv`, or scoop |

What ports across OSes vs. what's Linux-only in this memo:

- **Portable** (check in and reproduce anywhere): `pyproject.toml`, `uv.lock`,
  `.python-version`. `uv.lock` carries per-platform markers, so one lockfile
  resolves the right wheels on each OS at `uv sync` time. The uv commands
  themselves (`uv add`, `uv sync`, `uv run`, `uv tool install`, `uv python
  install`) are identical across OSes.
- **Linux-specific in this memo**: the shell recipes — `~/.local/bin/python3`
  wrapper, `#!/bin/sh` shebangs, `ssh <host>` invocations, absolute `/home/…`
  paths, `~/.bashrc` PATH exports. On macOS most translate verbatim (zsh
  instead of bash, `~/.zshrc`). On Windows the equivalent of the wrapper is
  a `.bat`/`.ps1` shim under `%USERPROFILE%\.local\bin\` — `uv python
  install --default` handles this automatically.
- **Managed Python builds**: `python-build-standalone` on Linux and macOS
  (ELF / mach-O; relocatable); MSVC-built CPython distributions on Windows.
  ABI is stable within a minor on all three, so the patch-bump
  auto-follow story applies everywhere.
- **Caveat already noted in the [Fleet](#fleet) section**: Intel MKL / `dpnp` / `dpctl`
  / `mkl-dpcpp` are x86_64-only. On Apple Silicon or ARM Linux, use the
  Accelerate framework (macOS) or OpenBLAS (Linux) via stock NumPy/SciPy
  wheels — no uv-side change needed.

### uv-managed Python as the user default

uv can own the user-level `python` / `python3` you get when `~/.local/bin`
precedes `/usr/bin` on `PATH` (see [Installing Python](https://docs.astral.sh/uv/guides/install-python/)):

```bash
uv python install --default 3.14     # writes ~/.local/bin/{python,python3,python3.14}
uv python upgrade 3.14               # rolls the same shims onto the newest patch
```

The shims dispatch through the minor-line symlink
(`~/.local/share/uv/python/cpython-3.14-linux-<arch>-gnu/bin/python3.14`), so
patch upgrades land automatically.

**Leave `/usr/bin/python3` alone.** Ubuntu wires the distro Python into apt,
`unattended-upgrades`, `command-not-found`, netplan, etc. Override only the
user-level default on `PATH`; never replace the system binary.

Caveat: uv Pythons are python-build-standalone builds — relocatable and mostly
static. ~99% drop-in, but a handful of native extensions that probe system
OpenSSL / libc paths can behave slightly differently from Ubuntu's
`python3-*` apt packages. Rare; flag if it bites.

### Package installation: the pip replacement story

Three layers, pick by use case:

1. **Project-managed (preferred).** `pyproject.toml` + `uv.lock` +
   `.python-version`, all operated on through [`uv add` / `uv remove`](https://docs.astral.sh/uv/concepts/projects/dependencies/),
   [`uv sync` / `uv lock`](https://docs.astral.sh/uv/concepts/projects/sync/).
   This is the default for everything under my short-name
   dirs (`~/e`, `~/i`, `~/k`, `~/p`, …). No `pip install` at all; the lockfile
   is the source of truth. Concept overview: [uv projects](https://docs.astral.sh/uv/concepts/projects/).
2. **[`uv pip`](https://docs.astral.sh/uv/pip/) — drop-in pip compatibility.** For ad-hoc venvs or scripts that
   predate a `pyproject.toml`. Same subcommands as pip, faster, same mental
   model; no lockfile involvement:

   ```bash
   uv pip install <pkg>          # into the active venv (or --python <path>)
   uv pip uninstall <pkg>
   uv pip list / uv pip freeze
   uv pip sync requirements.txt  # make venv exactly match a requirements file
   uv pip compile pyproject.toml -o requirements.txt   # pip-tools replacement
   ```

   Rule: `uv pip` operates on an **existing venv** — it won't touch
   `pyproject.toml` or `uv.lock`. Don't mix it into a project that's already
   `uv sync`-managed; the two views of "what's installed" will drift.
3. **[`uv tool` / `uvx`](https://docs.astral.sh/uv/concepts/tools/) — pipx replacement.** Global CLI tools (ruff, black,
   httpie, pre-commit…) in isolated envs, shims in `~/.local/bin`:

   ```bash
   uv tool install ruff          # persistent install + shim
   uv tool list / uv tool upgrade --all / uv tool uninstall ruff
   uvx ruff check .              # one-shot, ephemeral env (alias for uv tool run)
   uv run --with <pkg> <cmd>     # one-shot inside the current project context
   ```

Not used: `pip`, `pip-tools`, `pipx`, `virtualenv`, `venv` directly. uv covers
all of them.

### Always-on libraries in `python3` (scratch venv pattern)

Goal: a handful of libraries (`requests`, `httpx`, `rich`, …) always available
when I type `python3` at the shell, without polluting the clean uv-managed
interpreter. uv has no "install -U into the default Python" mode by design —
the substitute is a scratch uv project whose `.venv` backs `python3`:

```bash
mkdir -p ~/.local/py && cd ~/.local/py
uv init --bare --python 3.14
uv add requests                    # add more with `uv add <pkg>` any time
```

Then route `~/.local/bin/python3` at the scratch venv. **Symlink does NOT
work** — Python's venv detection walks up from `argv[0]` looking for
`pyvenv.cfg`; with a symlink at `~/.local/bin/python3`, `argv[0]` stays
outside `.venv/bin/` and no `pyvenv.cfg` is found, so `site-packages` isn't
on `sys.path`. Binary runs, but `import requests` → `ModuleNotFoundError`.
**Wrapper script** works because `exec` places `argv[0]` inside the venv:

```bash
rm -f ~/.local/bin/python3         # CRITICAL — see warning below
cat > ~/.local/bin/python3 <<'EOF'
#!/bin/sh
exec /home/mz0/.local/py/.venv/bin/python "$@"
EOF
chmod +x ~/.local/bin/python3
hash -r
python3 -V                         # => 3.14.x
python3 -c 'import requests; print(requests.__version__)'
```

> ⚠️ **`rm` the symlink first, never `cat >` through it.** If
> `~/.local/bin/python3` is already a symlink (e.g. created earlier by
> `uv python install --default`), `cat > ~/.local/bin/python3` opens the file
> for writing by *following* the symlink and overwrites the target — the
> managed Python binary at `~/.local/share/uv/python/cpython-X.Y.Z-.../bin/python3.X`.
> Every venv that routed through the minor-line alias now has a shell script
> where its interpreter should be, and invoking `python3` produces a shebang
> exec-loop until the kernel hits its recursion cap. Recovery is
> `uv python install --reinstall 3.14`.

`~/.local/bin/python` stays as the uv-default shim → clean managed Python
(no deps). Split of responsibilities: `python` for dep-free one-offs and
`uv run --with` experiments; `python3` for batteries-included interactive use.

Maintenance:

- **Add/upgrade a lib**: `cd ~/.local/py && uv add <pkg>` or `uv sync --upgrade`.
- **Patch-bump Python** (e.g. `uv python upgrade 3.14` from 3.14.3 → 3.14.4):
  nothing to do. `.venv/bin/python` is a symlink through uv's minor-line
  alias; next invocation of `python3` runs the new patch. `site-packages`
  stays valid (ABI-stable within a minor).
- **Minor-bump Python** (3.14 → 3.15): rebuild the venv.
  ```bash
  cd ~/.local/py && uv python pin 3.15 && rm -rf .venv && uv sync
  ```
- **Cross-host**: check `~/.local/py/{pyproject.toml,uv.lock,.python-version}`
  into a repo; `uv sync` on another host reproduces the scratch env. Wrapper
  script is per-host (paths are absolute).

## The three layers that decide which Python a uv project uses

1. **`.python-version`** — the project-level pin. Written by `uv python pin
   <X>`. `X.Y` is usually enough (e.g. `3.14`); uv picks the newest matching
   install. Commit this file.
2. **`requires-python`** in `pyproject.toml` — the *floor* for the package
   itself and for downstream consumers. uv refuses to build a venv below this.
3. **`.venv/bin/python`** — the concrete interpreter symlink. Regenerated by
   `uv sync` / `uv venv`. Don't hand-edit; treat `.venv/` as disposable.

Order of precedence when resolving: CLI `--python` > `.python-version` >
`requires-python` floor > uv default.

## uv's Python layout on disk

Under `~/.local/share/uv/python/` you'll see two kinds of entries:

- **Real install dirs** — `cpython-3.14.3-linux-x86_64-gnu/`, one per
  installed patch release. These are what uv downloads.
- **Minor-line symlinks** — `cpython-3.14-linux-x86_64-gnu -> cpython-3.14.3-...`,
  one per installed minor. **Managed by uv**, not by you. Created/updated
  whenever a patch is installed or when you run `uv python upgrade 3.14`, so
  the symlink always points at the newest installed patch for that minor.

And under `~/.local/bin/` (if you've run `uv python install --default` or
`uv python upgrade`), shims that route through the minor-line symlink:

```
~/.local/bin/python      -> .../cpython-3.14-.../bin/python3.14
~/.local/bin/python3.14  -> .../cpython-3.14-.../bin/python3.14
```

Implications for `.venv` longevity:

- If `.venv/bin/python` resolves through the **minor-line symlink** (e.g.
  `~/e/git-log-analysis`), it silently follows patch upgrades — no `uv sync`
  needed when 3.14.3 → 3.14.4.
- If it resolves to a **specific patch dir** (e.g. `~/i/QM1` → `cpython-3.14.2`),
  it breaks the moment that exact patch is uninstalled. `uv sync` rebuilds.
- `uv python pin 3.14` (minor) tends to produce the first kind;
  `uv python pin 3.14.2` (patch) produces the second. Prefer minor pins.

## Bump the Python version in a uv project

Changing the pin, not the venv:

```bash
cd <project>
uv python pin 3.14            # rewrites .python-version
# (optional) raise the floor in pyproject.toml:
#   requires-python = ">=3.14"
rm -rf .venv                  # optional; avoids stale symlinks and leftovers
uv sync                       # fetches the Python if missing, rebuilds .venv, installs deps
```

Gotchas:

- `uv sync` auto-installs a missing Python. Override with
  `python-preference = only-system` in `~/.config/uv/uv.toml` if you want the
  opposite.
- Crossing a feature line (e.g. 3.13 → 3.14) can shift dependency markers —
  `uv sync` relocks when needed; force with `uv lock --upgrade` if in doubt.
- Pin to `3.14` (not `3.14.3`) unless you need a specific patch: you get free
  patch upgrades next sync.
- `.venv/bin/python` is a symlink into `~/.local/share/uv/python/...`. If you
  `uv python uninstall` a version, every venv pointing at it breaks silently
  until next `uv sync`.

## Fix a broken `.venv`

Symptoms: `.venv/bin/python` is a dangling symlink; `uv run` / activation
errors with "no such file".

```bash
cd <project>
readlink -f .venv/bin/python           # confirm the target is missing
cat .python-version                     # what does the project want? (e.g. 3.13)
rm -rf .venv
uv sync                                 # uv installs the pinned Python if absent, then builds .venv
```

If the pin itself is stale (e.g. you're happy to move to the latest 3.13):

```bash
uv python pin 3.13        # keep 3.13 line, grab newest patch
# or bump to a different line entirely:
# uv python pin 3.14
rm -rf .venv && uv sync
```

## Everyday commands

Full flag reference: [uv CLI](https://docs.astral.sh/uv/reference/cli/).

```bash
# Python installs uv manages
uv python list                          # everything uv knows about (installed + downloadable)
uv python list --only-installed         # just what's on disk
uv python install 3.13                  # install latest 3.13.x
uv python install 3.13.11               # exact patch
uv python uninstall 3.13.11             # remove — will break any venv pinned to it

# Project lifecycle
uv init --python 3.14 my-proj           # new project with a pin
uv sync                                 # install/refresh deps into .venv per uv.lock
uv sync --upgrade                       # bump within version constraints
uv lock --upgrade-package <pkg>         # targeted bump
uv add <pkg>                            # add a dep and sync
uv remove <pkg>
uv run <cmd>                            # run inside the project venv without activating
uv tree                                 # dependency tree

# Ad-hoc venv outside a project
uv venv --python 3.14 .venv
source .venv/bin/activate
```

## urz: conda + Intel channel

Why `urz` has conda at all: it has an **Intel Tiger Lake Iris Xe** iGPU, and
Intel historically shipped its optimized Python stack — MKL-linked NumPy/SciPy,
`dpnp` (Data Parallel NumPy), `dpctl` (SYCL device control), `mkl-dpcpp`,
`intel-sycl-rt`, `intel-opencl-rt` — through its conda channel
(`software.repos.intel.com/python/conda`). PyPI wheels don't carry the same
builds, so `uv` can't be a drop-in replacement for these projects.

### Intel channel reality, as of 2026-05-07

Direct spot-check of `software.repos.intel.com/python/conda` (`win-64`,
`linux-64`, `noarch`) — Intel has **gutted** the channel. Only the
GPU/SYCL accelerators and oneAPI compiler runtimes remain:

| Still on the channel (2026-05) | Removed / no longer available |
|---|---|
| `dpctl` 0.21.0, `dpnp` 0.19.0 (both Oct 2025) | `intelpython3_full`, `intelpython3_core` |
| `daal4py` 2024.7.0 (stale, Sept 2024) | MKL-linked `numpy`, `scipy` |
| oneAPI compiler runtimes (`dpcpp`, `ifx`, `icc`, `impi`) | `mkl`, `mkl-service`, `mkl-dpcpp` |
| `intel-gpu-ocl-icd-system` (noarch) | `intel-sycl-rt`, `intel-opencl-rt` |
| `neural-compressor` (noarch) | `scikit-learn-intelex` |

**Implication for the Linux `idp` env**: it's preserved as installed but
**no longer reproducible from scratch** with the original recipe.
`intelpython3_full` and the MKL meta-packages aren't reachable anymore.
Don't `conda env remove -n idp` and expect to recreate it the same way.

**The new recipe** (for both Linux urz and Windows wig):

- `conda-forge` for the Python ecosystem (numpy, scipy, scikit-learn, pandas, …).
  conda-forge ships MKL-linked NumPy/SciPy when the `mkl` package is in the env.
- Intel channel **only** for `dpnp`/`dpctl` when GPU SYCL on Iris Xe is wanted.
- **`scikit-learn-intelex`** (conda-forge) replaces what `daal4py` used to do —
  patches sklearn at runtime to use oneDAL backends. Specifically accelerates
  `SVC`, `KMeans`, `RandomForest`, `LogisticRegression`. Two-line opt-in:
  ```python
  from sklearnex import patch_sklearn
  patch_sklearn()
  ```
  Available on conda-forge for Python 3.10–3.14 on win-64 (verified
  `2025.11.0` build, Mar 2026).

### Layout on urz

| Thing | Path / value | Notes |
|---|---|---|
| conda install | `/opt/conda` | root-owned, system-wide, **read-only base** |
| conda version | 26.3.2 | libmamba solver |
| base Python | 3.13.13 | do not install into base |
| system condarc | `/opt/conda/.condarc` | channels: `defaults` only |
| user condarc | `~/.condarc` | channels: Intel → conda-forge |
| effective channel order | Intel → conda-forge → defaults | per `conda info` |
| arch tag | `__archspec=1=icelake` | solver picks icelake-optimized builds |
| user envs | `~/.conda/envs/<name>/` | no sudo needed here |
| oneAPI redistributables | `/opt/intel/oneapi/redist/` | separate from conda |

### The read-only-base gotcha

Because `/opt/conda` is root-owned, any change to the **base** env
(including `conda update -n base ...`, installing into base, or updating
conda itself) needs sudo:

```bash
sudo /opt/conda/bin/conda update -n base conda           # update conda itself
sudo /opt/conda/bin/conda update -n base --all           # bump base pkgs
sudo /opt/conda/bin/conda clean --all                    # clear system pkg cache
```

Never `sudo conda` without the full `/opt/conda/bin/conda` path — sudo's PATH
may point at a different conda and you'll install into the wrong root.

Everything else (creating envs, installing into named envs, activating) runs
**without sudo**, because user envs live under `~/.conda/envs/` — that's what
makes the read-only-base setup tolerable:

```bash
/opt/conda/bin/conda create -n myproj python=3.12 numpy scikit-learn   # uses Intel channel via ~/.condarc
/opt/conda/bin/conda activate myproj                                    # or: source /opt/conda/etc/profile.d/conda.sh
/opt/conda/bin/conda install -n myproj dpnp dpctl mkl-dpcpp
/opt/conda/bin/conda env remove -n myproj
```

### Choosing conda vs uv on urz

Rule of thumb:

- **Conda env**, when the project leans on Intel-optimized numerics or GPU
  SYCL: anything that actually benefits from MKL-linked NumPy/SciPy, `dpnp`,
  `dpctl`, `mkl-dpcpp`, or needs `intel-sycl-rt`/`intel-opencl-rt` to reach
  the Iris Xe. Keep these in `~/.conda/envs/<name>/`.
- **uv project**, for everything else — pure-Python tools, web code,
  CLI utilities, anything where the PyPI wheel is already optimal. Same
  `pyproject.toml` + `uv.lock` as on `pug`.
- **Don't mix the two in one project.** Pick a home per project.

### What exists today (urz envs, as of 2026-04-21)

Two envs retained after the 2026-04-21 clean-up. Mtime is a staleness proxy.

| Env | Purpose | Jupyter kernelspec |
|---|---|---|
| `idp` | General data-science env (originally Intel Distribution for Python): `intelpython3_full` + pandas/matplotlib/plotly/catboost, MKL-linked numpy/scipy, `dpnp`/`dpctl`/`mkl-dpcpp` for SYCL on Iris Xe | `~/.local/share/jupyter/kernels/idp/` (display "idp"); plus `python3` kernel inside the env itself |
| `kbn` | LangChain / LangGraph / OpenAI stack **with** Jupyter. | `~/.local/share/jupyter/kernels/kbkern/` (display "kbn 3.13") |

Last cleanup 2026-04-21 — ≈7.9 GB reclaimed.

**`conda env remove` ToS gotcha (conda 26.x).** The removal may fail with
`CondaToSNonInteractiveError` for envs whose resolver touches
`repo.anaconda.com/pkgs/main` or `/pkgs/r`. Workaround: skip conda's
bookkeeping and delete the env dir directly — env removal is effectively
`rm -rf` anyway:

```bash
rm -rf ~/.conda/envs/<name>
```

Quick ways to re-inspect:

```bash
/opt/conda/bin/conda list -n <env> | grep -iE '^(intel|mkl|numpy|scipy|dpnp|dpctl)'
/opt/conda/bin/conda env remove -n <env>    # drop an env (or rm -rf, see above)
jupyter kernelspec list                     # which envs are registered as kernels
```
*uv* on `urz` was bootstrapped 2026-04-21 via the standard installer
(see [Fleet](#fleet) section). *uv* and *Conda* coexist fine as long as you don't try to manage
the same project with both. `uv` ignores `/opt/conda`
unless `CONDA_PREFIX` is active in the shell.

## urz-Windows: Pixi

Same hardware as Linux `urz` (Tiger Lake i7-1135G7, Iris Xe iGPU), Windows 11
boot. **Pixi** is the single tool — it handles what uv handles on `pug` *and*
what conda handles on Linux `urz`. One binary, one lockfile, conda-forge as
the primary channel, PyPI bridge for the rest.

### Why Pixi here (and not uv + conda mirrored from Linux)

- conda-forge already covers the full data-science stack on win-64
  (numpy, scipy, scikit-learn, pandas, jupyter, matplotlib, plotly, catboost).
  Pinning `mkl` in deps is enough to get MKL-linked NumPy/SciPy — no Intel
  channel needed for that anymore (see [Intel channel reality](#intel-channel-reality-as-of-2026-05-07)).
- `scikit-learn-intelex` on conda-forge gives the SVC / KMeans / RF
  acceleration that `daal4py` used to. Tracks Python 3.10 through 3.14.
- For pure-Python tooling (the uv side of the Linux split) Pixi has
  `pixi add --pypi <pkg>` and `pixi global install` for shims.
- Single lockfile (`pixi.lock`) instead of `uv.lock` + `conda env export`.

Trade-off: lockfiles aren't portable between Pixi and uv. The Windows `iap`
project's `pixi.lock` lives apart from any Linux uv lock. Don't try to share.

Naming note: the Windows env is `iap`, deliberately distinct from the
Linux env `idp` (whose name came from "Intel Distribution for Python",
now historical — see [Intel channel reality](#intel-channel-reality-as-of-2026-05-07)).

### MKL: when is it worth pinning?

- **Yes**, for the general `iap` env — Tiger Lake's AVX-512 makes MKL
  beat OpenBLAS by 10–30% on large GEMM, FFT, eigensolvers. A few hundred MB
  of disk is cheap.
- **No measurable effect** on `SVC`, decision trees, pure-pandas pipelines —
  those don't go through BLAS. `scikit-learn-intelex` is the relevant
  optimization for those.
- conda-forge selects the BLAS implementation by which package is in the
  env: pull `mkl` and `numpy`/`scipy` link against it; otherwise OpenBLAS.

### Install

```powershell
winget install prefix-dev.pixi
# adds %USERPROFILE%\.pixi\bin to PATH
pixi --version
```

Self-update later: `pixi self-update` or `winget upgrade prefix-dev.pixi`.

### Layout on Windows

| Thing | Path | Notes |
|---|---|---|
| Pixi binary | `%USERPROFILE%\.pixi\bin\pixi.exe` | Added to user PATH by installer |
| Global shims | `%USERPROFILE%\.pixi\bin\` | `ruff.exe`, `black.exe`, …; from `pixi global install` |
| Global envs | `%USERPROFILE%\.pixi\envs\<name>\` | One per `--environment` |
| Per-project env | `<project>\.pixi\envs\default\` | Created by `pixi install` |
| Package cache | `%LOCALAPPDATA%\rattler\cache\` | Shared across projects |

### `iap` env: project-local, Python 3.14

Single env for all data-science / ML tasks under `C:\e\yageweek`.
Lives in the repo so the lockfile travels with code (rule from
[Parity rules across the fleet](#fleet)).

The env is defined as a Pixi *feature* named `iap`, so the on-disk path
is literally `.pixi\envs\iap\` (parallel to Linux `~/.conda/envs/idp/`).
Trade-off: every Pixi command needs `-e iap`.

```toml
# C:\e\yageweek\pyproject.toml
[project]
name = "yageweek"
version = "0.1.0"
description = "AgentsWeek task solutions"
requires-python = ">=3.14"

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["win-64"]

[tool.pixi.activation.env]
PYTHONUTF8 = "1"               # Windows quirk: forces UTF-8 stdout/stdin

[tool.pixi.feature.iap.dependencies]
python = "3.14.*"
mkl = "*"                                              # MKL runtime
libblas   = { version = "*", build = "*mkl" }          # required: see "Pinning MKL" below
libcblas  = { version = "*", build = "*mkl" }
liblapack = { version = "*", build = "*mkl" }
numpy = "*"
scipy = "*"
scikit-learn = "*"
scikit-learn-intelex = "*"     # oneDAL acceleration; patches SVC, KMeans, RF
pandas = "*"
joblib = "*"
matplotlib = "*"
plotly = "*"
catboost = "*"
jupyter = "*"
ipykernel = "*"

[tool.pixi.environments]
iap = ["iap"]
```

Bootstrap and run:

```powershell
cd C:\e\yageweek
pixi install -e iap                                       # creates .pixi\envs\iap\
pixi run -e iap python entry\taskB-runes\runes-SVM.py     # uses the env
pixi shell -e iap                                          # interactive activation
```

### Activation modes (analogs of `conda activate`)

Three ways to put commands inside a pixi env, in increasing order of "stickiness":

| Mode | What it does | Closest conda analog |
|---|---|---|
| `pixi run -e <env> <cmd>` | Runs one command inside the env; current shell unchanged | `conda run -n <env> <cmd>` |
| `pixi shell -e <env>` | Spawns a new `$SHELL` with the env active; `exit` returns | `conda activate <env>` + `conda deactivate`, bracketed by a shell process |
| `eval "$(pixi shell-hook -e <env>)"` | Mutates the **current** shell — sets PATH, env vars, any `[tool.pixi.activation.env]` keys (e.g. `PYTHONUTF8=1`) | `conda activate <env>` proper |

There's no `pixi deactivate`. Pixi's design steers you to the sub-shell
pattern — interactive work in `pixi shell`, one-offs in `pixi run`, and
`shell-hook` only when activation has to happen inside the current shell
(a CI step, a sourced dotfile, a script that can't spawn a sub-shell).
To "deactivate" after `shell-hook`, open a new shell.

On Windows PowerShell the form is `pixi shell-hook -e iap | Out-String | Invoke-Expression`.

### Pinning MKL (mandatory, not optional)

`mkl = "*"` alone gets the MKL runtime DLLs into the env but **does not**
make NumPy use them. conda-forge's BLAS shims (`libblas`/`libcblas`/`liblapack`)
ship multiple builds — `*_netlib` (reference), `*_openblas`, `*_mkl`, `*_blis`,
`*_accelerate` — and the solver picks one based on what else is in the env.
Without an explicit build pin you can end up with `*_netlib` (reference, slow)
even though MKL is installed. Hit this on the first solve here.

The fix is the three-line build-string pin shown in the recipe:
```toml
libblas   = { version = "*", build = "*mkl" }
libcblas  = { version = "*", build = "*mkl" }
liblapack = { version = "*", build = "*mkl" }
```

Verify NumPy actually picked it up:

```powershell
pixi run -e iap python -c "import numpy as np; _ = np.random.randn(200,200) @ np.random.randn(200,200); import psutil; p = psutil.Process(); [print(m.path) for m in p.memory_maps() if 'mkl_' in m.path.lower()]"
```

Should list `mkl_core.2.dll`, `mkl_intel_thread.2.dll`, `mkl_rt.2.dll`, and on
Tiger Lake also `mkl_avx512.2.dll` (AVX-512 dispatch). `numpy.show_config()`
isn't enough on Windows — it always reports the netlib shim names; the actual
implementation reveals itself in loaded DLLs.

### Windows quirks (worth knowing once)

- **`PYTHONUTF8=1`** — Windows defaults Python's stdout to `cp1252`. Any
  `print()` of non-Latin-1 text (Cyrillic, ideographs, em-dashes) crashes
  with `UnicodeEncodeError`. Setting `PYTHONUTF8=1` (PEP 540) at the env
  level fixes it once for all scripts run via `pixi run -e iap`.
- **Always invoke through `pixi run -e iap` (or `pixi shell -e iap`).**
  Direct invocation of `.pixi\envs\iap\python.exe` from a plain PowerShell
  exits 127 with no output the moment numpy tries to load MKL — the env's
  `Library\bin\` isn't on PATH, so the DLL search fails. Pixi's `run`/`shell`
  set this up; bypassing them is a Windows-specific footgun. (VS Code's
  Python extension activates the env correctly when the interpreter is
  selected, so F5 / debug just works.)
- **Line endings** — pandas' `to_csv` writes `\r\n` on Windows; if you
  diff against a reference CSV authored on Linux, hashes will differ but
  content is identical. Compare with `Get-Content` (line-aware) or
  `Compare-Object`, not `Get-FileHash`.
- **`scikit-learn-intelex` + `joblib.parallel_backend("threading")`** —
  sklearnex doesn't support the `threading` backend and emits a UserWarning
  per fit (i.e. once per CV fold × candidate). Harmless — sklearnex falls
  back to "all available threads" via TBB anyway. Either drop the
  `parallel_backend` block from scripts that target sklearnex, or run with
  `python -W ignore` to silence the noise.

### Optional: GPU SYCL on Iris Xe

Skip until needed. To add later, extend the project with the Intel channel:

```toml
[tool.pixi.project]
channels = ["https://software.repos.intel.com/python/conda", "conda-forge"]

[tool.pixi.dependencies]
dpnp = "*"
dpctl = "*"
```

The Iris Xe compute runtime on Windows comes from the **Intel Graphics Driver**
(or the oneAPI Base Toolkit) — system-installed, not via Pixi.
Different model from Linux, where `intel-opencl-rt` came in via the env.

### VS Code

1. Install the Microsoft **Python** extension.
2. Optional: **Pixi** extension by prefix-dev — auto-detects `pyproject.toml`
   with `[tool.pixi]`, surfaces tasks.
3. `Ctrl+Shift+P` → *Python: Select Interpreter* →
   `.pixi\envs\iap\python.exe`. (On Windows Pixi puts `python.exe` directly
   at the env root, not under `Scripts\`.)
4. Run scripts with F5 or `pixi run -e iap python ...`.

### Reproducibility files (commit these)

- `pyproject.toml` — deps and channels (`[project]` + `[tool.pixi.*]`)
- `pixi.lock` — full transitive resolution, all `platforms` listed
- `.python-version` — minor pin (advisory under Pixi; `pixi.lock` wins)

`.gitignore`: `.pixi/`, `__pycache__/`, `*.egg-info/`.

### Coexistence rules

- Don't manage a project with both Pixi and uv — pick one per project
  (same rule as uv-vs-conda on Linux, see [Choosing conda vs uv on urz](#choosing-conda-vs-uv-on-urz)).

## pug: uv -> pixi migration plan

### Install pixi

```bash
# suggest mise alternative for ease of updates
pixi --version
```

`/usr/bin/python3` (3.12.3, owned by apt) stays untouched. Pixi only owns `~/.pixi/`.

### Always-on `python3`: pixi global env

Replaces uv's `~/.local/py` scratch venv. Same package list (`requests`).

```bash
pixi global install \
  --environment py \
  --expose python3=python \
  --expose python=python \
  python=3.14 \
  requests
```

Builds `~/.pixi/envs/py/`, writes activation shims at `~/.pixi/bin/{python,python3}`.
No wrapper script, no `pyvenv.cfg` symlink trap, no risk of overwriting the
managed binary (the failure mode flagged in the uv scratch-venv section).
Add libs later with `pixi global install --environment py <pkg>`.

### Per-project envs

One `pyproject.toml` per project. Pin Python via a feature;
`pixi install -e <env>` produces `pixi.lock`. Example shape (e.g. `~/i/QM1`):

```toml
[project]
name = "qr-maker"
version = "0.1.0"
requires-python = ">=3.14"

[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64"]

[tool.pixi.feature.qm1.dependencies]
python = "3.14.*"
segno = "*"

[tool.pixi.environments]
qm1 = ["qm1"]
```

Run: `pixi run -e qm1 python script.py`. Commit `pyproject.toml` + `pixi.lock`;
gitignore `.pixi/`.

PyPI-only deps go under `[tool.pixi.feature.<name>.pypi-dependencies]`.
Workspace-shaped repos (`~/k/krisp-2025` with `backend`/`frontend` members)
need a separate per-project sketch — pixi's multi-package model differs from
uv workspaces; flag when getting there.

### Procedural mitigations

The project env and the global env live at separate paths and don't share
`site-packages`. The leak — project code imports a lib that's only in the
global env, project's own `pyproject.toml` doesn't declare it, project ships
broken — only happens if you bypass pixi and call the global `python3`
against project code.

- **Always invoke project code through `pixi run -e <env>` or
  `pixi shell -e <env>`.** Bare `python script.py` from inside a project dir
  falls through to the global shim and can silently satisfy a missing dep.
- **VS Code: pin the project interpreter.**
  `Ctrl+Shift+P → Python: Select Interpreter → .pixi/envs/<env>/bin/python`
  per project. F5 / debug then route correctly.
- **Keep the global env minimal.** `requests` and not much else; small surface
  = small mask. Add to a project, not to global, when in doubt.
- **Never `pip install` into a pixi-managed env.** Lockfile and reality drift;
  pixi has no way to recover the manifest from `site-packages`.

These mitigations apply equally to the uv scratch-venv pattern — same leak
shape, same fixes (substitute `uv run` for `pixi run`).

### Detection mitigations

[`deptry`](https://github.com/fpgmaas/deptry) parses source imports and diffs
against `pyproject.toml`. Install as a global tool, not a per-project dep:

```bash
pixi global install --environment dev deptry
```

Run per project:

```bash
cd ~/i/QM1
deptry .
```

Findings:

- **DEP001** — used but not declared (the leak case)
- **DEP002** — declared but unused
- **DEP003** — used as transitive (declared by a dep, not by you)

Wire into `.pre-commit-config.yaml` per project:

```yaml
- repo: https://github.com/fpgmaas/deptry
  rev: 0.21.0
  hooks:
    - id: deptry
```

CI (where projects have it): one step that runs `deptry .` on every push.
A clean CI run becomes a structural promise that the project doesn't lean
on the global env.

### Tooling layout after the switch

| Thing | Path | Notes |
|---|---|---|
| Pixi binary | `~/.pixi/bin/pixi` | `pixi self-update` for upgrades |
| Global env `py` | `~/.pixi/envs/py/` | Backs `~/.pixi/bin/python3` |
| Global env `dev` | `~/.pixi/envs/dev/` | Holds `deptry`, future lint/format tools |
| Per-project envs | `<project>/.pixi/envs/<name>/` | Disposable; `pixi install -e <name>` rebuilds |
| Package cache | `~/.cache/rattler/` | Shared across all projects |
| System python3 | `/usr/bin/python3` | Untouched, owned by apt |

### What never exists under this plan

No `~/.local/share/uv/`, no `~/.local/bin/uv`, no `uv.lock` anywhere, no
`~/.local/py/` scratch project + wrapper script, no `--break-system-packages`.
One tool, one binary, one lockfile shape per project.

## TODO / open threads

- Policy for when to bump `requires-python` floor vs. just the pin.
- `~/e/git-log-analysis` has no `.python-version`; decide whether to pin.
- PyCharm on `urz` still has dead interpreter registrations for the dropped envs.
  Let PyCharm notice and repoint the live projects
  (e.g. `~/p/let-a-tin`) at their new `.venv/bin/python`;
  prune the dead ones via the PyCharm interpreter settings UI.
- `~/.conda/envs/etc/aau_token` — not a real env, purpose unknown.
  ```
    # same day as /opt/conda
  22 2025-09-19 22:05:53 +0400 ~/.conda/envs/etc/aau_token

   6 2025-09-19 14:21:02 +0400 /opt/conda/envs/
  17 2025-09-19 14:20:59 +0400 /opt/conda/x86_64-conda-linux-gnu/
  ```
- ~~Bootstrap `wig`~~ **done 2026-05-07**: Pixi 0.66.0 installed via winget,
  `iap` env solved and built (`.pixi\envs\iap\`) with MKL-backed NumPy
  (verified `mkl_avx512.2.dll` loads on Tiger Lake).
- The Linux `idp` recipe in this memo is now historical — `intelpython3_full`
  isn't reachable from a fresh install. (?? is it true?).
  If urz-Linux's `idp` ever needs rebuilding, port it to the same
  conda-forge + `mkl` + `scikit-learn-intelex` recipe
  that wig uses (with `dpnp`/`dpctl` from the Intel channel).
