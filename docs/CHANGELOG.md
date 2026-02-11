# Changelog

This project uses a curated changelog to highlight notable changes by release.
Detailed commit history remains available in GitHub.

The format is based on the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) guidelines,
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [Unreleased]

### Changed

- The documentation for this project is being updated to a more modern and intuitive theme,
  layout, and structure. The intent is to be less verbose and instead make the documentation 
  more human-oriented with helpful guides and tutorials.

---
## [1.4.0] - 2026-02-04

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

<!-- TODO: Continue populating the changelog from the original file -->

<!-- The reference definitions are listed below -->
[Unreleased]: https://github.com/jeffshurtliff/salespyforce/compare/1.4.0...HEAD
[1.4.0]: https://github.com/jeffshurtliff/salespyforce/releases/tag/1.4.0
