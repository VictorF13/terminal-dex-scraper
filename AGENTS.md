# AGENTS.md

This project uses:

- **uv** for all dependency management and running scripts  
- **prek** for pre-commit checks and running all code quality tools  
- **ruff** for linting and formatting  
- **basedpyright** for type checking  

Configuration lives in:
- `pyproject.toml` (ruff + pyright rules)  
- `.pre-commit-config.yaml` (prek hooks for ruff, basedpyright, and updating requirements and uv.lock)  

There are no tests.

## Setup
```sh
uv sync
prek install
```

## Running the app

Always use `uv run`:

```sh
uv run path/to/script.py
```

## Dependency management

Use only `uv`:

* Add runtime: `uv add PACKAGE`
* Remove runtime: `uv remove PACKAGE`
* Add dev: `uv add --dev PACKAGE`
* Remove dev: `uv remove --dev PACKAGE`
* Sync lockfile/env: `uv sync`

## Code quality

All quality checks (ruff + basedpyright) must be run through `prek`:

```sh
prek run --all-files
```

Or target specific paths:

```sh
prek run src/
prek run file.py
```

## Commit rules

Use Conventional Commits without parentheses:

* `feat: add feature`
* `fix: correct bug`
* `chore: update deps`
* `docs: update docs`
* `refactor: simplify code`
* `perf: improve performance`
* `style: apply formatting`

## Guardrails

* Do not call `pip`, `python`, `ruff`, or `basedpyright` directly. Always go through `uv` and `prek`.
* Keep diffs minimal and consistent with existing style.
* If in doubt, run `prek run --all-files` to validate.
