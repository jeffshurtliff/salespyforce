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

- The {py:func}`salespyforce.utils.version.get_version_from_pyproject` function was 
  added as a fallback method for retrieving the current package version when the 
  package is not installed.

(unreleased-changed)=
### Changed

- The {py:func}`salespyforce.utils.version.get_full_version` and 
  {py:func}`salespyforce.utils.version.get_major_minor_version` functions now attempt to 
  retrieve the version from the `pyproject.toml` file if it cannot be retrieved via the 
  package metadata.
- The documentation for this project has updated to a more modern and intuitive theme,
  layout, and structure. The intent was to be less verbose and instead make the documentation 
  more human-oriented with helpful guides and tutorials.
    - The previous Sphinx content has been preserved in `docs_legacy/` for historical purposes.

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
  versus a ``None`` value.
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
[Unreleased]: https://github.com/jeffshurtliff/salespyforce/compare/1.4.0...HEAD
[1.4.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.2...1.3.0
[1.2.2]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.1...1.2.2
[1.2.1]: https://github.com/jeffshurtliff/salespyforce/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.2...1.2.0
[1.1.2]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.1...1.1.2
[1.1.1]: https://github.com/jeffshurtliff/salespyforce/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/jeffshurtliff/salespyforce/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/jeffshurtliff/salespyforce/releases/tag/1.0.0
