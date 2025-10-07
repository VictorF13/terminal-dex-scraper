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

## Dev environment tips
```sh
uv sync
prek install
```

- Always use `uv run path/to/script.py` instead of `python`.

## Dependency instructions
Use only `uv` for dependencies:
- Add runtime: `uv add PACKAGE`
- Remove runtime: `uv remove PACKAGE`
- Add dev: `uv add --dev PACKAGE`
- Remove dev: `uv remove --dev PACKAGE`
- Sync lockfile/env: `uv sync`

## Code quality checks
Run all checks (ruff + basedpyright) through `prek`:
```sh
prek run --all-files
```
Or target a specific file:
```sh
prek run --files path/to/file.py
```

## Docstring rules
All non-private functions should have a docstring in this format:

```py
"""One liner of what the function does. First verb imperative.

May or may not have other paragraphs explaining more stuff. Make sure to
adhere to the maximum amount of text per line, breaking things up only
when it's over 88 characters.

Args:
    argument_name (argument_type, optional): What the argument is.
        Defaults to <something> in case it's optional. Use a 4 character
        indentation when breaking lines in either Args, Returns or Raises.
    another_argument (argument_type): What this argument represents.

Returns:
    type_of_return: What it returns.

Raises:
    ErrorType: Only if the `raise` is written in this function/method.

"""
```

Notes:
- Include **Args** only if the function has arguments.  
- Include **Returns** only if it returns something other than `None`.  
- Include **Raises** only if the function explicitly raises the error.  

## Commit instructions
Use Conventional Commits without parentheses:
- `feat: add feature`
- `fix: correct bug`
- `chore: update deps`
- `docs: update docs`
- `refactor: simplify code`
- `perf: improve performance`
- `style: apply formatting`

## Guardrails
- Do not call `pip`, `python`, `ruff`, or `basedpyright` directly. Always go through `uv` and `prek`.
- Keep diffs minimal and consistent with existing style.
- If in doubt, run `prek run --all-files` to validate.
