# GEMINI.md

`AGENTS.md` is the canonical contributor guide for this repository. **Read it
first and follow it in full** — every rule in it applies to Antigravity and
Gemini CLI. This file adds only the notes that are specific to working here with
Gemini and Antigravity tooling.

Keep it that way: if a rule applies to every agent or contributor, put it in
`AGENTS.md`, not here. This file should stay short and never contradict
`AGENTS.md`.

## Environment and commands

- Dependency management and builds use **Poetry** (see `AGENTS.md` →
  "Dev environment"). Supported Python: 3.12 and 3.13.
- Before handing work back, run and report the same checks CI runs:
  - `poetry run ruff check .`
  - `poetry run ruff format --check .`
  - `poetry run pytest -q`
- Integration tests need real org credentials and are opt-in. Do not run
  `--integration` unless the user asks and a helper file is available.

## Header block attribution

When you change a file whose header block has `:Last Modified:` / `:Modified Date:`
(Python modules) or `Last Modified By:` / `Modified Date:` (shell scripts), update
them per `AGENTS.md` → "Module header blocks". For Antigravity and Gemini CLI specifically:

- Modifier field → `<orchestrating person> (via <exact model id>)`, e.g.
  `Jeff Shurtliff (via gemini-3.7-flash)` or `Jeff Shurtliff (via gemini-3.7-pro)`.
  Use the real model ID you are running as (for example `gemini-3.7-flash`,
  `gemini-3.7-pro`, `gemini-3-flash-lite`), not a marketing name. If the person
  prefers not to be named, use `Anonymous (via <model id>)`.
- Date field → today's local date, matching the existing format (`DD Mon YYYY`
  in Python headers, `YYYY-MM-DD` in shell scripts).
- Only touch these fields on files you actually changed.

## Secrets — never read, print, or commit

See `AGENTS.md` → "Secrets and local-only files". Treat these as off-limits:
`local/`, `$HOME/secrets/`, `.env*`, and `.github/encrypted/*.gpg`. They hold
real Salesforce credentials. Never open them, echo their contents, paste them
into code/docs/commit messages, or add real credentials to any tracked file. Use
`examples/helper.yml` (placeholder values) as the reference.

## Git

- Work on a branch, never directly on `master`. Branch prefixes and the
  issue-number convention are in `CONTRIBUTING.md` (`feature/`, `fix/`,
  `refactor/`, `chore/`, `docs/`, `test/`, `ci/`, `security/`).
- Do not commit or push unless the user asks.
- Commit messages: past tense ("Added ...", "Fixed ..."), focused, and mention
  the file name when it reads naturally.
- Update `docs/CHANGELOG.md` under `[Unreleased]` for any user-visible change.

## Working style and Antigravity features

- Plan non-trivial changes before editing; this project values small, localized,
  well-tested diffs over broad refactors.
- When you add or change a public function/method/class, add the
  `.. versionadded::` / `.. versionchanged::` directive using the **stable**
  version derived from `pyproject.toml` (e.g. `2.0.0.dev0` → `2.0.0`). See
  `AGENTS.md` → "Version directives".
- Project skills live under `.agents/skills/` (e.g.
  `salespyforce-stable-release-prep`), which Antigravity automatically
  discovers. Custom rules can be placed in `GEMINI.md` or `.agents/rules/`.
- Follow the pre-submit checklist in `AGENTS.md` before wrapping up.
