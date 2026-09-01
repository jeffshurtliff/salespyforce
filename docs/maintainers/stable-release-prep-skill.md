(maintainer-stable-release-prep-skill)=
# Using the SalesPyForce Stable Release Prep Skill

The repository includes an agent skill for preparing a development or prerelease
version of SalesPyForce as a stable release candidate. The skill coordinates the
reversible preparation and validation work in the {doc}`releasing` runbook while
preserving the runbook's approval boundaries for repository history and external
publication.

The skill is stored at:

```text
.agents/skills/salespyforce-stable-release-prep/
```

Codex and Antigravity scan `.agents/skills` from the working directory through the
repository root, so this placement makes the skill available throughout the
checkout. See
[OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills) for
current discovery and invocation behavior.

Claude Code discovers project skills under `.claude/skills/<name>/SKILL.md`
instead. The repository exposes the same skill to Claude Code through a symlink:

```text
.claude/skills/salespyforce-stable-release-prep -> ../../.agents/skills/salespyforce-stable-release-prep
```

The symlink keeps a single canonical copy of `SKILL.md`, the inspector script,
and the agent metadata; there is nothing to keep in sync between the two paths.
Contributors on filesystems without symlink support (for example a Windows
checkout without symlinks enabled) can still direct any agent to read
`.agents/skills/salespyforce-stable-release-prep/SKILL.md` manually.

It is repository-owned and contains no credentials, private helper data, local
filesystem paths, or maintainer-specific environment configuration.

## When to use the skill

Use the skill when promoting the static version in `pyproject.toml` from a
development or prerelease value, such as `2.0.0.dev0`, to its intended stable
version, such as `2.0.0`.

Do not use it for routine dependency updates, ordinary development-version
bumps, prerelease publication, or projects outside the SalesPyForce repository.

The runbook remains authoritative. Read {doc}`releasing` before beginning a
release window, particularly when continuing beyond local preparation.

## Prerequisites

Before invocation, confirm that:

- the repository is available in a clean working tree;
- the intended release work has been merged into `master`;
- a **Maintainer Release** tracking issue
  (`.github/ISSUE_TEMPLATE/maintainer-release.md`) has been opened and the exact
  stable version has been identified;
- Poetry and the project's development dependencies are installed; and
- read-only access to GitHub and PyPI is available for duplicate-version checks.

Credentials for later publication must remain outside the repository and must
never be pasted into an agent prompt, command, issue, pull request, artifact, or
release note.

## Invoke the skill

From a compatible agent working at the repository root, invoke the skill by its
name and provide the target version and issue number:

```text
Use $salespyforce-stable-release-prep to prepare SalesPyForce 2.0.0 from
2.0.0.dev0 using issue #123. Complete all local preparation and validation,
then stop before staging, committing, pushing, tagging, or publishing anything.
```

In Codex, reference the skill with `$salespyforce-stable-release-prep` as shown
above. In Claude Code, invoke it with `/salespyforce-stable-release-prep` or let
it trigger automatically from a matching request; the same version and issue
details still need to be supplied. In Antigravity, the skill is automatically
discovered under `.agents/skills/` and can be invoked directly or triggered on
demand.

Replace the example values with the approved release values. Supplying the
previous stable tag is optional when it can be established unambiguously from
reachable Git history and the changelog.

Agents that do not automatically discover repository skills can be directed to
read `.agents/skills/salespyforce-stable-release-prep/SKILL.md` before performing
the same request.

## Default scope

The preparation request authorizes the skill to:

- perform local and read-only remote preflight checks;
- create or use the policy-compliant local release branch;
- promote the Poetry version and finalize the changelog;
- update version-sensitive maintained documentation when needed;
- run lint, formatting, test, documentation, build, and artifact checks;
- smoke-test the built wheel in clean temporary virtual environments; and
- report candidate artifact names and SHA-256 checksums.

The preparation request does **not** authorize the skill to:

- create or modify a GitHub issue or pull request;
- stage, commit, merge, or push changes;
- create or push a tag;
- upload to TestPyPI or PyPI; or
- create, edit, publish, or delete a GitHub Release.

Each later action requires explicit authorization. Approval for one action does
not imply approval for the next.

## Expected result

On successful completion, the skill returns a release-readiness report with:

- the resolved version, date, tags, branch, and release scope;
- the files changed and the reason for each change;
- pass, fail, or skipped status for every required check;
- the candidate source distribution and wheel checksums;
- any unresolved blocker or manual review; and
- the next action that requires maintainer authorization.

The working tree should contain only deliberate release-preparation changes.
Generated distributions and Sphinx output must remain ignored and unstaged.

## Continue after preparation

After reviewing the local changes, authorize later actions separately and name
their exact scope. For example:

```text
Using $salespyforce-stable-release-prep, stage and commit only the validated
release-preparation files for issue #123. Do not push the branch.
```

A later request may authorize pushing the branch and creating a pull request.
Tagging, TestPyPI, production PyPI, and GitHub Release operations remain separate
checkpoints. Before each action, the agent must reread the corresponding section
of {doc}`releasing` and revalidate its prerequisites.

Candidate archives built before the preparation pull request is merged must
never be reused for publication. Publication artifacts must be rebuilt from the
exact, synchronized, CI-verified commit on `master`.

## Artifact inspector

The skill includes a deterministic archive inspector. After a clean Poetry
build, it can be run directly from the repository root:

```bash
python3 .agents/skills/salespyforce-stable-release-prep/scripts/inspect_release_artifacts.py \
  --expected-version "2.0.0" \
  --strict
```

The inspector verifies the SalesPyForce distribution name and version, required
source files, wheel metadata, expected archive counts, suspicious secret or local
configuration paths, package code, and SHA-256 checksums. Strict mode treats
suspicious archive warnings as failures.

This check supplements `poetry run twine check --strict`; it does not replace
Twine, clean-environment installation, CI, or manual release review.

The release workflow uses separate environments for wheel smoke tests. The
first installs with `--no-deps` and validates distribution metadata. The second
installs the wheel normally with its runtime dependencies before importing the
public `Salesforce` client. A dependency-free environment is not expected to
import the client successfully.

## Maintaining the skill

When the release workflow changes, update these sources together:

- `.agents/skills/salespyforce-stable-release-prep/SKILL.md` (the canonical copy;
  the `.claude/skills/` entry is a symlink and needs no separate edit);
- the included artifact inspector when archive rules change;
- `.github/ISSUE_TEMPLATE/maintainer-release.md` when the release phases or
  authorization checkpoints change;
- {doc}`releasing`; and
- this usage guide.

If the skill directory is ever renamed or moved, update the
`.claude/skills/salespyforce-stable-release-prep` symlink target to match.

Validate the skill structure with the agent platform's skill validator when one
is available. Always run Ruff against the Python helper, build the Sphinx
documentation with warnings treated as errors, and exercise the inspector
against both valid and deliberately invalid temporary artifacts.
