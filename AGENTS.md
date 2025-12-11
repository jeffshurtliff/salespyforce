# Agent Guidelines for `salespyforce`

These instructions apply to all work in this repository.

## Development practices
- Follow PEP 8 conventions for Python code, but line lengths may exceed 79
  characters when it improves clarity.
- Prefer explicit, secure defaults: avoid disabling SSL verification unless
  absolutely required, do not log secrets, and validate inputs received from
  configuration files or environment variables.
- Keep changes backward compatible with the public API exposed by the
  `salespyforce.Salesforce` class unless a breaking change is explicitly
  requested.
- When handling HTTP interactions, use `requests` session objects where
  available to reuse connections and apply common headers or auth settings.

## Repository layout
- Package code lives under `src/salespyforce/`; examples are under
  `examples/`; documentation sources reside in `docs/`.
- README.md contains quick-start guidance and should remain synchronized with
  any changes to primary workflows or configuration expectations.

## Testing and quality
- Run `pytest` to exercise the test suite when altering behavior.
- Run `bandit -r src` for security linting on Python changes.
- Ensure new functionality is covered by tests when feasible.

## Dependency and build tooling
- Dependencies are defined in `pyproject.toml`; prefer updating them there and
  regenerating lock files as needed.
- Use Poetry commands for local environment tasks when possible (e.g.,
  `poetry install`, `poetry run pytest`).

## Documentation expectations
- Inline code comments should clarify intent without repeating obvious logic.
- For new public methods or parameters, update or create docstrings and keep
  documentation consistent with behavior shown in README and docs.
