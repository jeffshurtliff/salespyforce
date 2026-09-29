# Changelog

This project uses a curated changelog to highlight notable changes by release.
Detailed commit history remains available in GitHub.

The format is based on the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
(relnotes-unreleased)=
## [Unreleased]

(unreleased-added)=
### Added

No unreleased additions at this time.

(unreleased-changed)=
### Changed

- The docstrings across the codebase were rewritten to align with current best practices and to 
  provide additional clarity and improve user experience.
- The {py:exc}`~salespyforce.errors.exceptions.GETRequestError` exception is now raised instead of the 
  generic {py:exc}`RuntimeError` exception if a GET request does not return a successful response.
  - Similar changes have also been implemented for POST, PATCH, PUT, and DELETE requests.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_articles_list` method (and the underlying
  {py:func}`salespyforce.knowledge.get_articles_list` function) can now return a ``list`` of article 
  data (default) or the full API response in JSON format.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_validation_status` method (and the underlying
  {py:func}`salespyforce.knowledge.get_validation_status` function) will now raise a {py:exc}`TypeError` 
  exception if the article details are an invalid data type and cannot be parsed.
- Fixed an issue in {py:func}`salespyforce.knowledge.update_article` and
  {py:func}`salespyforce.knowledge.publish_article` where API responses for PATCH requests were being 
  incorrectly converted to JSON format.
- The {py:func}`salespyforce.knowledge.publish_multiple_articles` function now always returns the full 
  {py:class}`requests.Response` object for the API response.
- The {py:exc}`~salespyforce.errors.exceptions.DataMismatchError` exception is now raised when posting a
  Chatter feed item or comment if both message text and message segments are provided, or if provided 
  message segments are not properly structured.
- The {py:func}`salespyforce.knowledge.archive_article` function can now return a Boolean value indicating 
  whether the archival was successful (default), or the full API response from the PATCH request.
- Updated {py:func}`salespyforce.utils.core_utils.get_random_string` to use the cryptographically secure 
  ``secrets`` module instead of the standard ``random`` module and included additional validations.
- The {py:func}`salespyforce.utils.core_utils.get_18_char_id` function now raises a {py:exc}`TypeError`
  exception instead of {py:exc}`ValueError` if the record ID provided is not a string.
- Updated how loggers are initialized in each module to ensure proper logging functionality.
- Added a default timeout to Salesforce API requests to prevent connections from waiting indefinitely.
- Type hints and docstrings have been updated globally to reflect current best practices.
- POST, PATCH, and PUT requests made through {py:func}`salespyforce.api.api_call_with_payload` now
  raise the JSON decoding exception if a non-empty response body is not valid JSON, consistent with
  GET and DELETE requests, rather than printing a message and returning the raw response.
- Disabled the Ruff ``E501`` (line too long) lint rule in ``pyproject.toml`` and removed the
  now-unnecessary ``# noqa: E501`` comment; ``ruff format`` still enforces the 130-character line
  length for code, and has been applied to the modules that were not yet compliant.
- Updated the unit tests for the API, core utilities, and Knowledge modules to reflect the
  method-specific request exceptions, the ``secrets``-based random string generation, the
  {py:exc}`TypeError` raised for non-string record IDs, and the ``return_json`` argument passed
  when publishing articles.

(unreleased-security)=
### Security

No unreleased security updates at this time.

---
(relnotes-2.0.1)=
## [2.0.1] - 2026-09-20

SalesPyForce 2.0.1 is a patch release that raises the `soupsieve` dev-dependency
floor to address two security advisories and adds contributor-guide support for
Antigravity and Gemini CLI. There are no runtime API changes.

(relnotes-2.0.1-added)=
### Added

- Added `GEMINI.md` companion guide to support Antigravity and Gemini CLI workflows.

(relnotes-2.0.1-changed)=
### Changed

- Updated `AGENTS.md`, `.gemini/settings.json`, and maintainer skill documentation
  to reference `GEMINI.md` and Antigravity support.

(relnotes-2.0.1-security)=
### Security

- Raised the `soupsieve` dev-dependency floor to `>=2.9.0` (locked at 2.9.2) to address
  CVE-2026-85999 and CVE-2026-86000.

---
(relnotes-2.0.0)=
## [2.0.0] - 2026-08-30

SalesPyForce 2.0.0 is the first stable release of the 2.x line. It drops support
for Python 3.9, 3.10, and 3.11, modernizes security-sensitive dependency
constraints, and adds the maintainer release runbook and the repeatable stable
release preparation skill.

```{warning}
SalesPyForce `2.0.0` and newer require Python `3.12` or newer. SalesPyForce
`1.5.0` is the final release that supports Python `3.9`, `3.10`, and `3.11`.
```

(relnotes-2.0.0-added)=
### Added

- Added the `docs/maintainers/releasing.md` document with maintainer instructions for
  preparing a stable release for distribution.
- Added the repository-owned `$salespyforce-stable-release-prep` skill and
  maintainer usage guide for repeatable, approval-gated stable release preparation.
  The skill is discoverable by both Codex (`.agents/skills/`) and Claude Code
  (`.claude/skills/`, symlinked to the canonical copy).
- Added a **Maintainer Release** issue template
  (`.github/ISSUE_TEMPLATE/maintainer-release.md`) and made a dedicated release
  tracking issue a required prerequisite in the maintainer release runbook.

(relnotes-2.0.0-changed)=
### Changed

- Dropped Python 3.9, 3.10, and 3.11 support; SalesPyForce 2.x supports Python 3.12
  and 3.13.
- Simplified security-sensitive dependency constraints after dropping older Python
  support, including modern Requests, urllib3, and pytest floors and removal of the
  `tomli` backport.
- Updated CI, Read the Docs, maintained documentation, and Ruff configuration for
  the Python 3.12+ support baseline.
- Corrected the release wheel smoke-test procedure to separate dependency-free
  metadata validation from dependency-aware public API import validation.

(relnotes-2.0.0-removed)=
### Removed

- Removed the deprecated {py:func}`salespyforce.utils.core_utils.display_warning`
  function, which was deprecated in 1.4.0 and scheduled for removal in 2.0.0. Use
  {py:func}`salespyforce.errors.handlers.display_warning` instead.

(relnotes-2.0.0-security)=
### Security

- Constrained development environments to setuptools 83.0.0 or newer to address
  the `MANIFEST.in` exclusion bypass caused by Unicode normalization collisions
  in source distributions on macOS.
- Constrained development environments to `cryptography` 50.0.0 or newer to address
  CVE-2026-69247 (GHSA-g6cj-pr64-35w5), a Bleichenbacher oracle in PKCS#7
  `EnvelopedData` decryption. Cryptography is a development-only dependency pulled
  in transitively through Twine's keyring integration and is not used at runtime
  by SalesPyForce.

---
(relnotes-1.5.0)=
## [1.5.0] - 2026-07-22

This release adds new utilities, improves API and Knowledge behavior, centralizes
package constants, modernizes documentation and quality tooling, and refreshes
security-sensitive dependency constraints.

```{warning}
SalesPyForce `2.0.0` and newer require Python 3.12 or newer.

SalesPyForce `1.5.0` is the final release supporting Python 3.9, 3.10, and 3.11.
```

(relnotes-1.5.0-added)=
### Added

- The {py:func}`salespyforce.utils.version.get_version_from_pyproject` function was 
  added as a fallback method for retrieving the current package version when the 
  package is not installed.
- The {py:exc}`salespyforce.errors.exceptions.PATCHRequestError` exception class has
  been added to leverage with PATCH request exceptions.
- The {py:func}`~salespyforce.utils.core_utils.ensure_starts_with` and 
  {py:func}`~salespyforce.utils.core_utils.ensure_ends_with` core utility functions have 
  been added to assist with input validation.

(relnotes-1.5.0-changed)=
### Changed

- Successful GET, POST, PATCH, PUT, and DELETE responses with empty bodies are now
  returned as raw response objects instead of being passed to JSON decoding. This
  prevents successful `204 No Content` DELETE operations from raising JSON decode
  errors.
- The {py:meth}`salespyforce.Salesforce.patch` method once again defaults
  `return_json` to `False`, preserving the public behavior released in version 1.4.0.
- String helper paths now infer JSON or YAML parsing from their `.json`, `.yml`, or
  `.yaml` file extensions. Explicit sequence, set, and mapping helper forms remain
  supported.
- Knowledge article publishing now uses the centralized
  `REST_PATHS.ARTICLE_MASTER_VERSION_BY_ID` endpoint template.
- Regression coverage has been added for API response handling, Knowledge and Chatter
  endpoint construction, helper file selection, and API request exception messages.
- Adopted Ruff for linting, import sorting, and formatting; added project configuration,
  replaced flake8 validation in CI, and documented the contributor quality checks.
- CI now verifies the security-sensitive dependency versions selected for each Python
  release, isolates pytest temporary files, and validates built artifacts with Twine.
- Added prominent README and Sphinx documentation notices that version 1.5.0 is
  the final release supporting Python 3.9 through 3.11 and that version 2.0.0
  requires Python 3.12 or newer.
- The constants used by the package have been centralized within the new 
  {py:mod}`salespyforce.constants` module and the other modules have been updated accordingly.
- The {py:meth}`~salespyforce.Salesforce.download_image` method now logs errors and raises exceptions 
  when failing to successfully download an image.
- The {py:func}`salespyforce.utils.version.get_full_version` and 
  {py:func}`salespyforce.utils.version.get_major_minor_version` functions now attempt to 
  retrieve the version from the `pyproject.toml` file if it cannot be retrieved via the 
  package metadata.
- The {py:meth}`salespyforce.Salesforce.Knowledge.delete_article_draft` method (and underlying function)
  now supports the `sobject` parameter to specify the sObject against which to query.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_validation_status` method (and underlying function) 
  now includes the `use_knowledge_articles_endpoint` parameter so you can specify the REST path to utilize.
- The following methods (and underlying functions) now raise the 
  {py:exc}`~salespyforce.errors.exceptions.MissingRequiredDataError` exception rather than generic 
  {py:exc}`RuntimeError` or {py:exc}`ValueError` exceptions when required data is missing:
  - {py:meth}`salespyforce.Salesforce.Chatter.post_feed_item`
  - {py:meth}`salespyforce.Salesforce.Chatter.post_comment`
  - {py:meth}`salespyforce.Salesforce.Knowledge.get_article_url`
  - {py:meth}`salespyforce.Salesforce.Knowledge.create_draft_from_master_version`
  - {py:meth}`salespyforce.Salesforce.Knowledge.publish_multiple_articles`
- The {py:meth}`salespyforce.utils.core_utils.download_image` function now raises more specific 
  exceptions instead of the generic {py:exc}`RuntimeError` exception.
  - The {py:exc}`salespyforce.errors.exceptions.MissingRequiredDataError` exception is raised if 
    neither an image URL nor an API response are provided when calling the function.
  - The {py:exc}`salespyforce.errors.exceptions.GETRequestError` exception is raised if the GET 
    request fails to download the image.
- The {py:func}`salespyforce.utils.helper.import_helper_file` and
  {py:func}`salespyforce.utils.helper.get_helper_settings` functions now support both `yml` and
  `yaml` extensions for YAML files.
- The documentation for this project has updated to a more modern and intuitive theme,
  layout, and structure. The intent was to be less verbose and instead make the documentation 
  more human-oriented with helpful guides and tutorials.
    - The previous Sphinx content has been preserved in `docs_legacy/` for historical purposes.
- The test suite has been moved from `src/salespyforce/utils/tests/` to the root-level
  `tests/` directory to better align with standard Python project layout practices.
- The root-level test suite is now organized into `tests/unit/` and
  `tests/integration/` to separate deterministic unit coverage from opt-in
  environment-dependent integration coverage.

(relnotes-1.5.0-removed)=
### Removed

- The {py:class}`salespyforce.utils.helper.HelperParsing` class has been removed as its functionality 
  has been replaced by the `YAML_BOOLEAN_MAPPING` constant in the {py:mod}`salespyforce.constants`
  module.

(relnotes-1.5.0-security)=
### Security

- Updated `idna` to 3.15 or newer to address CVE-2026-45409 on every supported
  Python version.
- Constrained the documentation dependencies to `soupsieve` 2.8.4 or newer to
  address CVE-2026-49476 and CVE-2026-49477. Soup Sieve remains required
  transitively by the PyData Sphinx Theme through Beautiful Soup.
- Constrained development and documentation environments to Pygments 2.20.0 or
  newer to address CVE-2026-4539.
- Python 3.10 and newer now require Requests 2.33.0 or newer, urllib3 2.7.0 or
  newer, and pytest 9.0.3 or newer to address CVE-2026-25645,
  CVE-2026-44431, CVE-2026-44432, and CVE-2025-71176.
- Python 3.9 retains the newest compatible Requests, urllib3, and pytest release
  lines because the corresponding fixed releases require Python 3.10 or newer.
  SalesPyForce does not use Requests' vulnerable `extract_zipped_paths()` utility
  or directly invoke urllib3's affected low-level proxy redirect and streaming
  APIs. pytest is development-only, and the Python 3.9 CI jobs use an isolated,
  owner-only temporary directory on ephemeral runners.
- Version 1.5.0 is the final SalesPyForce release supporting Python versions below
  3.12. Version 2.0.0 removes these Python 3.9 dependency exceptions and raises
  the minimum supported Python version to 3.12.

---
(relnotes-1.4.0)=
## [1.4.0] - 2026-02-04

(relnotes-1.4.0-added)=
### Added

- Several new methods have been introduced within the core object to perform various tasks:
    - The {py:meth}`~salespyforce.Salesforce.delete` method performs DELETE API calls.
    - The {py:meth}`~salespyforce.Salesforce.get_latest_api_version` method retrieves the 
      latest Salesforce API version.
    - The {py:meth}`~salespyforce.Salesforce.retrieve_current_user_info` method retrieves 
      information for the current/running user that was leveraged to connect to the 
      Salesforce REST API.
        - This method now runs during the core object instantiation so that the running user 
          information can be utilized as default parameter values with certain methods/functions.
    - Several new methods were added to check the user access for a specific record:
        - {py:meth}`~salespyforce.Salesforce.can_access_record`
        - {py:meth}`~salespyforce.Salesforce.can_read_record`
        - {py:meth}`~salespyforce.Salesforce.can_edit_record`
        - {py:meth}`~salespyforce.Salesforce.can_delete_record`
    - The {py:meth}`~salespyforce.Salesforce.get_18_char_id` method converts a 15-character 
      `Id` value into a valid 18-character value.
- Added several new functions in the utilities modules:
    - The new {py:meth}`salespyforce.utils.core_utils.is_valid_salesforce_url` function 
      is now utilized to ensure that URLs passed to the API call methods (e.g., 
      {py:meth}`~salespyforce.Salesforce.get`, {py:meth}`~salespyforce.Salesforce.put`, etc.) 
      to ensure they are valid Salesforce URLs. 

(relnotes-1.4.0-changed)=
### Changed

- The {py:class}`~salespyforce.Salesforce` client now defines and stores the `org_id` (str)  
  and `current_user_info` (dict) for use in client API calls as default parameter values.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_validation_status` method has been updated
  to use a more specific exception class, and to return an empty string on lookup failures 
  versus a `None` value.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_article_details` method now accepts the 
  optional `use_knowledge_articles_endpoint` parameter, which forces the `knowledgeArticles` 
  endpoint to be used for the GET request rather than the `sobjects` endpoint.
- The client methods for API calls (e.g. {py:meth}`~salespyforce.Salesforce.get`, 
  {py:meth}`~salespyforce.Salesforce.post`, etc.) now support passing full URLs as the endpoint 
  as long as they are valid Salesforce.com URLs.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_articles_list` method now logs errors 
  using the logger rather than writing to `stderr` in the console.

(relnotes-1.4.0-deprecated)=
### Deprecated

- The function {py:func}`salespyforce.utils.core_utils.display_warning` has been deprecated  
  and has been moved to {py:func}`salespyforce.errors.handlers.display_warning` instead.

(relnotes-1.4.0-fixed)=
### Fixed

- A logic issue was found and resolved in the 
  {py:meth}`salespyforce.Salesforce.Knowledge.get_article_id_from_number` method.

(relnotes-1.4.0-security)=
### Security

- Several dependency versions were updated to mitigate known vulnerabilities 
  found in earlier versions:
    - Explicitly pinned `urllib3` to require version `1.26.19` or above (below v3) 
      in order to avoid CVE-2024-37891.
    - Explicitly pinned `idna` to require version `3.7` or above (below v4) in order
      to avoid CVE-2024-3651.
    - Explicitly pinned `certifi` to require version `2024.7.4` or above in order to
      mitigate CA removals (e-Tugra, GLOBALTRUST) per CVE-2023-37920 and CVE-2024-39689.

---
(relnotes-1.3.0)=
## [1.3.0] - 2025-11-11

(relnotes-1.3.0-added)=
### Added

- The new {py:meth}`salespyforce.Salesforce.Knowledge.archive_article` method was added to 
  easily archive knowledge articles.

(relnotes-1.3.0-changed)=
### Changed

- The `next_records_url` parameter was added to the {py:meth}`~salespyforce.Salesforce.soql_query`
  method which introduces the ability to query using a `nextRecordsUrl` value.

---
(relnotes-1.2.2)=
## [1.2.2] - 2023-11-14

(relnotes-1.2.2-changed)=
### Changed

- The {py:meth}`salespyforce.Salesforce.Knowledge.check_for_existing_article` method has been 
  updated to introduce the `include_archived ` parameter, which specifies whether archived 
  articles will be included in the query results.

---
(relnotes-1.2.1)=
## [1.2.1] - 2023-09-01

(relnotes-1.2.1-changed)=
### Changed

- The {py:meth}`salespyforce.Salesforce.Knowledge.publish_article` method now returns a Boolean
  value by default, which indicates whether the operation was successful. It is still possible 
  to optionally return the full API response.

---
(relnotes-1.2.0)=
## [1.2.0] - 2023-08-31

(relnotes-1.2.0-added)=
### Added

- The new {py:meth}`salespyforce.Salesforce.Knowledge.assign_data_category` method has been added,
  which introduces the ability to assign data categories to a knowledge article draft.

(relnotes-1.2.0-fixed)=
### Fixed

- The underlying function for the {py:meth}`salespyforce.Salesforce.Knowledge.get_article_url` method
  was updated to fix an extraneous slash issue.

---
(relnotes-1.1.2)=
## [1.1.2] - 2023-06-05

(relnotes-1.1.2-changed)=
### Changed

- Only the version was changed in this release to address an issue with PyPI distribution.

---
(relnotes-1.1.1)=
## [1.1.1] - 2023-06-05

(relnotes-1.1.1-changed)=
### Changed

- Only the version was changed in this release to address an issue with PyPI distribution.

---
(relnotes-1.1.0)=
## [1.1.0] - 2023-05-29

(relnotes-1.1.0-added)=
### Added

- The {py:meth}`~salespyforce.Salesforce.get_org_limits` method was added to retrieve 
  the governor limits for the connected Salesforce org.
- The {py:meth}`~salespyforce.Salesforce.search_string` method was added to introduce
  the ability to perform a SOSL query to search for a given string.

---
(relnotes-1.0.0)=
## [1.0.0] - 2023-05-08

This was the first release of the `salespyforce` package on PyPI with its original 
features and functionality.


<!-- The reference definitions are listed below -->
[Unreleased]: https://github.com/jeffshurtliff/salespyforce/compare/2.0.1...HEAD
[2.0.1]: https://github.com/jeffshurtliff/salespyforce/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.5.0...2.0.0
[1.5.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.4.0...1.5.0
[1.4.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.2...1.3.0
[1.2.2]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.2...1.2.0
[1.1.2]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/jeffshurtliff/salespyforce/releases/tag/1.0.0
