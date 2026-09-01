# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Gemini CLI, etc.) and human
contributors working in this repository.

## How these instructions are organized

This file is the **canonical, tool-agnostic guide**. Everything here applies to
every agent and to human contributors.

Tool-specific notes live in thin companion files that point back here and add
only what is unique to that tool:

- `CLAUDE.md` — Claude Code
- `GEMINI.md` — Antigravity / Gemini CLI
- `.gemini/settings.json` — Gemini CLI (configured to read `GEMINI.md` as its context)

Rule of thumb for keeping things in sync: if guidance applies to more than one
tool, it belongs **here**, not in a companion file. Companion files should stay
short and never contradict this document.

`CONTRIBUTING.md` is the authoritative reference for the branch/issue/PR workflow
and the full documentation policy. This file summarizes the parts an agent needs
day to day and defers to `CONTRIBUTING.md` for the rest.

## Project overview

This repository contains `salespyforce`, a Python package/toolset for interacting
with Salesforce APIs. The public entry point is the `salespyforce.Salesforce`
client, which centralizes authentication, API-version selection, and access to
feature helpers (Chatter, Knowledge).

Primary goals when making changes:

- Keep the public API stable unless the change explicitly requires a breaking change.
- Prefer small, testable, localized changes over broad refactors.
- Keep docs and docstrings consistent and Sphinx-friendly.
- Never weaken security or introduce insecure defaults (see "Security" below).

## Dev environment

Use **Poetry** for dependency management and packaging. Supported Python versions
are **3.12 and 3.13** (`salespyforce` 2.x); do not add code that targets older
versions.

Common commands (prefer these unless the user asks otherwise):

- Install: `poetry install` (add `--with dev` to match CI)
- Run tests: `poetry run pytest -q`
- Run a subset: `poetry run pytest tests/unit -q`
- Lint: `poetry run ruff check .`
- Auto-fix lint: `poetry run ruff check . --fix`
- Format: `poetry run ruff format .`
- Format check (what CI runs): `poetry run ruff format --check .`
- Build: `poetry build`

If you add a dependency, add it via Poetry (`poetry add ...` /
`poetry add --group dev ...`) rather than editing `pyproject.toml` by hand, and
regenerate `poetry.lock` through Poetry.

### Linting and formatting

Ruff handles linting, import sorting, and formatting. Key settings (see
`pyproject.toml` for the source of truth):

- Line length: `130` characters. Keep code, tests, and normal strings at or under
  this. Wrap comments and docstrings when it helps readability.
- Use a targeted per-line `# noqa: E501` for the rare approved exception; never a
  file-level or global ignore.
- Format style: single quotes, spaces, LF line endings.
- `docs_legacy/` is excluded from Ruff and is retained for reference only — do
  not modify it.

CI enforces `ruff check .` and `ruff format --check .`.

## Secrets and local-only files

This project authenticates against real Salesforce orgs. Treat the following as
**off-limits** — never open, print, echo, paste into code/docs/commit messages,
or otherwise surface their contents, and never add real credentials to any
tracked file:

- `local/` — untracked; contains real helper configuration files with live credentials
- `$HOME/secrets/` — where CI and local scripts decrypt helper files at runtime
- `.env`, `.envrc`, and similar
- `.github/encrypted/*.gpg` — encrypted helper files; the passphrase is a CI secret

When you need a configuration reference, use `examples/helper.yml`, which
contains only placeholder (`xxxxx`) values. Documentation examples must use
obviously fake placeholder values for usernames, org IDs, URLs, client IDs,
client secrets, and tokens.

`.github/scripts/decrypt_helper*.sh` and `encrypt_secret.sh` manage the encrypted
helper files; do not run or modify them unless explicitly asked.

## Files not to edit by hand

- `poetry.lock` — regenerate via Poetry
- `src/salespyforce.egg-info/` — build-generated
- `dist/`, `.coverage`, `coverage.xml`, `.ruff_cache/`, `.pytest_cache/` — generated
- `docs_legacy/` — kept for historical reference only

## Coding style

- Prefer clarity over cleverness.
- Keep functions small and focused; avoid unnecessary abstraction.
- Keep changes localized; don't reformat or restructure unrelated code.
- Use type hints where they improve readability and tooling, especially for
  public APIs. Modules use `from __future__ import annotations`.
- Follow the existing module layout: core client in `core.py`, low-level request
  helpers in `api.py`, feature helpers in `chatter.py` / `knowledge.py`, shared
  utilities under `utils/`, errors under `errors/`, package-wide constants in
  `constants.py`.

## Docstrings (PEP 257 + Sphinx/reST)

### PEP 257 essentials (what "good" looks like)

Follow PEP 257 conventions:
- Use triple double-quotes: """..."""
- One-line docstrings:
  - The summary is on one line and ends with a period.
  - Example: """Return the API version string."""
- Multi-line docstrings:
  - First line is a short summary (imperative mood is fine), ending with a period.
  - Blank line after the summary.
  - Then a more detailed description if needed.
- Docstrings describe "what/why"; code should show "how".
- Keep docstrings updated when behavior changes.

### Sphinx/reST field list style (required)

Use Sphinx/reST field lists for parameters and returns:

- :param <name>: ...
- :type <name>: ... (only if the type is non-obvious or you're not using type hints consistently)
- :returns: ...
- :rtype: ... (only if needed; type hints usually suffice)
- :raises <ExceptionType>: ...

If type hints are present and clear, you may omit :type: and :rtype:.

### Function/method docstring template

```python
def example(name: str, enabled: bool = True) -> int:
    """Compute the example value.

    Longer explanation if needed.

    :param name: The user-facing name to process.
    :param enabled: Whether to enable additional processing.
    :returns: The computed example value.
    :raises ValueError: If `name` is empty.
    """
```

### Package / module docstrings (including __init__.py)

#### Module docstrings (some_module.py)

Every public module should start with a module docstring describing purpose and key concepts:

```
"""Salesforce REST helpers.

This module contains low-level request/response helpers used by the core client.
"""
```

#### Package docstrings (__init__.py)

If src/salespyforce/__init__.py exposes the public API (re-exports classes/functions),
include a package docstring that explains the package purpose and lists key exports.

```
"""Top-level package for salespyforce.

This package provides the :class:`salespyforce.Salesforce` client and related helpers.
"""
```

If __init__.py only marks a package and exports nothing meaningful, keep the docstring short
(or omit it).

### Class docstrings vs __init__ docstrings (important rule)

#### Preferred approach for user-facing classes

For user-facing classes, document constructor parameters in the class docstring (not duplicated in __init__), using :param: fields.

```python
class Salesforce:
    """Salesforce API client.

    :param username: API username.
    :param password: API password.
    :param org_id: Salesforce Org ID.
    :param base_url: Base instance URL (e.g. https://example.my.salesforce.com).
    :param endpoint_url: OAuth token endpoint URL.
    :param client_id: Connected App client ID.
    :param client_secret: Connected App client secret.
    :param security_token: Salesforce security token (if required).
    """
    def __init__(
        self,
        username: str,
        password: str,
        org_id: str,
        base_url: str,
        endpoint_url: str,
        client_id: str,
        client_secret: str,
        security_token: Optional[str] = None,
    ) -> None:
        """Initialize the client.

        Parameter documentation is defined on the class docstring.
        """
```

#### When __init__ should have full :param: docs

Only put full :param: documentation on __init__ if:
- the class docstring is intentionally minimal, or
- the class is internal/private and only __init__ needs documentation, or
- you need to document multiple alternative init signatures/behaviors that are clearer at __init__.

### Properties

Use property docstrings as short descriptions. Avoid :param: fields (properties take no params).

```python
@property
def api_version(self) -> str:
    """The Salesforce API version in use."""
```

### Version directives (`versionadded` / `versionchanged`)

Public functions, methods, classes, decorators, and exceptions carry Sphinx
version directives in their docstrings so the API reference shows when each entry
point appeared or last changed.

- **New public callable** → add `.. versionadded:: X.Y.Z`.
- **Changed public callable** (behavior, signature, parameters, return value,
  raised exceptions, or defaults) → add `.. versionchanged:: X.Y.Z` with a short
  note describing what changed. Keep any existing directives and append the new
  one.
- Always use the **stable** version the change will ship in — never the
  in-development version string. Derive it from the `version` field in
  `pyproject.toml` by dropping any dev/pre-release suffix:
  - `2.0.0.dev0` → `2.0.0`
  - `2.1.0rc1` / `2.1.0.rc0` → `2.1.0`
  - `2.0.3` (already stable) → `2.0.3`
- Place the directive(s) at the end of the docstring, after the field list
  (`:param:` / `:returns:` / `:raises:`), separated by a blank line.
- Private/internal items (leading underscore) do not get version directives.
- Pure internal refactors, renames, and doc-wording fixes do not get version
  directives — record those in `docs/CHANGELOG.md` instead.

```python
def bulk_upsert(records: list[dict], external_id: str) -> dict:
    """Upsert records by their external ID.

    :param records: The records to upsert.
    :param external_id: The external ID field name.
    :returns: The Salesforce composite response.
    :raises ValueError: If `records` is empty.

    .. versionadded:: 2.0.0
    """
```

When that function is later changed, append (do not replace) a
`.. versionchanged::` line:

```python
    :raises ValueError: If `records` is empty.

    .. versionadded:: 2.0.0
    .. versionchanged:: 2.1.0
       Added retry handling for transient `503` responses.
    """
```

## Tests

- Test suites live at the repository root under `tests/unit/` and
  `tests/integration/`.
- Add or update tests for behavior changes; add a regression test for every bug fix.
- Prefer pytest-style tests. Keep tests deterministic and isolated (no real
  network calls unless explicitly requested).
- Integration tests are opt-in: they are skipped unless `--integration` is passed
  and a helper file is available (`local/helper_dm_conn.yml` or
  `$HOME/secrets/helper_dm_conn.yml`). Do not attempt to run them without one.
  Run with `poetry run pytest --integration tests/integration -q`.
- CI enforces a minimum total coverage threshold of 50%.

## Documentation expectations

- If you change public behavior, update the docstrings and any relevant docs
  under `docs/`, and add an entry to `docs/CHANGELOG.md`.
- `docs/CHANGELOG.md` uses "Keep a Changelog" sections. Add user-facing entries
  under `## [Unreleased]` in the matching `Added` / `Changed` / `Deprecated` /
  `Removed` / `Fixed` / `Security` subsection.
- Internal-only refactors, tooling, CI, and dependency updates go in the
  CHANGELOG, not in narrative docs or version directives.
- Use Sphinx version directives (`.. versionadded::`, `.. versionchanged::`,
  `.. deprecated::`) only for changes to public behavior, signatures, return
  values, exceptions, or defaults. Every new or changed public callable needs
  one — see "Version directives" under "Docstrings" for the exact rule and which
  version number to use.
- In Markdown/MyST (`.md`) files, delimit inline code with a single backtick on
  each side. Do not use reStructuredText-style double-backtick delimiters in
  Markdown files (double backticks remain correct in `.rst` files and reST
  docstrings).
- Keep examples minimal, realistic, runnable, and limited to the public API with
  placeholder credentials.
- The `docs/` build uses Sphinx + MyST; `docs_legacy/` is a retired build kept
  for reference only.

### Module header blocks

When creating a new module, include a header block like the example below:

```python
# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.new_module_name
:Synopsis:          Defines the functionality related to ????
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     31 Dec 2025
"""
```

If you change any file with a header block containing `Last Modified` /
`Modified Date` (Python modules) or `Last Modified By` / `Modified Date` (shell
scripts):

- Update the modifier field with the name (or username/pseudonym) of the person
  orchestrating the change — the human developer directing the AI-generated
  changes, not the tool. Use `Anonymous` if the person prefers not to be named.
- Indicate which AI tool and/or model was used, in parentheses after the name,
  e.g. `John Doe (via GPT-5.2-Codex)`, `johndoe434 (via claude-sonnet-5)`. Each
  companion file pins the exact identifier format for its tool.
- Update the date field with the current local date, matching the existing
  format (`DD Mon YYYY` in Python headers, `YYYY-MM-DD` in shell scripts).
- Only update these fields on files you actually changed.

## Branch, commit, and PR hygiene

`CONTRIBUTING.md` has the full rules; the essentials:

- Branch from `master`; never commit directly to `master`.
- Branch names: `<prefix>/<issue-number>-short-description`, where `<prefix>` is
  one of `feature/`, `fix/`, `refactor/`, `chore/`, `docs/`, `test/`, `ci/`,
  `security/`.
- Do not commit or push unless the user asks.
- Keep commits focused and descriptive; prefer past tense ("Updated the ..." over
  "Update the ..."). Mention the file name when it fits organically.
- Don't change formatting in unrelated files. Avoid large refactors unless requested.
- Every PR should reference a GitHub Issue and use the matching branch prefix.
- For suspected vulnerabilities, use GitHub Private Vulnerability Reporting — do
  not open a public issue or include exploit details, payloads, or secrets.

## Security

`salespyforce` handles authentication flows and API tokens. Contributions must:

- Never log secrets (usernames, passwords, tokens, client secrets, session IDs).
- Avoid insecure defaults; keep SSL verification on by default.
- Validate user input where applicable.
- Justify any cryptographic or authentication change.
- Keep security-sensitive dependency floors (see `pyproject.toml` and the CI
  "Verify security dependency versions" step) intact or higher.

## Pre-submit checklist

Before handing work back or opening a PR:

1. `poetry run ruff check .`
2. `poetry run ruff format --check .`
3. `poetry run pytest -q`
4. Docstrings and `docs/` updated for any public-behavior change.
5. `.. versionadded::` / `.. versionchanged::` (stable version) added to every new
   or changed public callable.
6. `docs/CHANGELOG.md` `[Unreleased]` updated for any user-facing change.
7. Header blocks updated on changed files only.
8. No secrets or real credentials added to tracked files.
