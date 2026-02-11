# Changelog

This project uses a curated changelog to highlight notable changes by release.
Detailed commit history remains available in GitHub.

The format is based on the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
(relnotes-unreleased)=
## [Unreleased]

(unreleased-changed)=
### Changed

- The documentation for this project is being updated to a more modern and intuitive theme,
  layout, and structure. The intent is to be less verbose and instead make the documentation 
  more human-oriented with helpful guides and tutorials.

---
(relnotes-1.4.0)=
## [1.4.0] - 2026-02-04

(relnotes-1.4.0-added)=
### Added

- Several new methods have been introduced within the core object to perform various tasks:
    - The {py:meth}`salespyforce.Salesforce.delete` method performs DELETE API calls.
    - The {py:meth}`salespyforce.Salesforce.get_latest_api_version` method retrieves the 
      latest Salesforce API version.
    - The {py:meth}`salespyforce.Salesforce.retrieve_current_user_info` method retrieves 
      information for the current/running user that was leveraged to connect to the 
      Salesforce REST API.
        - This method now runs during the core object instantiation so that the running user 
          information can be utilized as default parameter values with certain methods/functions.
    - Several new methods were added to check the user access for a specific record:
        - {py:meth}`salespyforce.Salesforce.can_access_record`
        - {py:meth}`salespyforce.Salesforce.can_read_record`
        - {py:meth}`salespyforce.Salesforce.can_edit_record`
        - {py:meth}`salespyforce.Salesforce.can_delete_record`
    - The {py:meth}`salespyforce.Salesforce.get_18_char_id` method converts a 15-character 
      `Id` value into a valid 18-character value.
- Added several new functions in the utilities modules:
    - The new {py:meth}`salespyforce.utils.core_utils.is_valid_salesforce_url` function 
      is now utilized to ensure that URLs passed to the API call methods (e.g. 
      {py:meth}`salespyforce.Salesforce.get`) to ensure they are valid Salesforce URLs. 

(relnotes-1.4.0-changed)=
### Changed

- The {py:class}`salespyforce.Salesforce` client now defines and stores the `org_id` (str)  
  and `current_user_info` (dict) for use in client API calls as default parameter values.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_validation_status` method has been updated
  to use a more specific exception class, and to return an empty string on lookup failures 
  versus a ``None`` value.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_article_details` method now accepts the 
  optional `use_knowledge_articles_endpoint` parameter, which forces the `knowledgeArticles` 
  endpoint to be used for the GET request rather than the `sobjects` endpoint.
- The client methods for API calls (e.g. {py:meth)`salespyforce.Salesforce.get`, 
  {py:meth)`salespyforce.Salesforce.post`, etc.) now support passing full URLs as the endpoint 
  as long as they are valid Salesforce.com URLs.
- The {py:meth}`salespyforce.Salesforce.Knowledge.get_articles_list` method now logs errors 
  using the logger rather than writing to `stderr` in the console.

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
## 1.3.0 - 2025-11-11

Coming soon!

<!-- TODO: Continue populating the changelog from the original file -->

<!-- The reference definitions are listed below -->
[Unreleased]: https://github.com/jeffshurtliff/salespyforce/compare/1.4.0...HEAD
[1.4.0]: https://github.com/jeffshurtliff/salespyforce/releases/tag/1.4.0
