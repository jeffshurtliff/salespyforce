##########
Change Log
##########
This page documents the additions, changes, fixes, deprecations and removals made in each release.

***********
v1.4.0.dev2
***********
**Release Date: TBD**

Added
=====

Core Object
-----------
Additions to the :doc:`core-object-methods` are listed below.

* Added the :py:meth:`salespyforce.core.Salesforce.get_latest_api_version` method which retrieves
  the latest API version by querying the authorized Salesforce org, returning the version as a
  string (e.g. ``65.0``)
* Added the ``FALLBACK_SFDC_API_VERSION`` constant that is leveraged if the
  :py:meth:`salespyforce.core.Salesforce.get_latest_api_version` method fails to retrieve the
  latest API version for the authorized Salesforce org

Primary Modules
---------------
Additions to the :doc:`primary modules <primary-modules>` are listed below.

* Added the :py:func:`salespyforce.api.delete` function to perform DELETE API requests.

Supporting Modules
------------------
Changes to the :doc:`supporting modules <supporting-modules>` are listed below.

* Added the :py:mod:`salespyforce.utils.tests.conftest` module to configure pytest for unit testing.
* Added the :py:mod:`salespyforce.utils.tests.test_core_utils` module to test the core utilities.
* Added the :py:mod:`salespyforce.utils.tests.test_log_utils` module to test the logging functionality.

General
-------
* Created the ``.readthedocs.yaml`` file to manage the integration with the ReadTheDocs documentation
* Added the new ``.github/workflows/ci.yml`` CI workflow to follow best practices and improve deployments
* Added the ``docs/ci.md`` Markdown document with CI-related instructions and notes
* Added the ``.github/scripts/decrypt_helper_local.sh`` script to assist with pytest and CI
* Added the ``AGENTS.md`` file to define agent guidelines with the package

Changed
=======

Core Object
-----------
Changes to the :doc:`core-object-methods` are listed below.

* Updated the docstring for the :py:meth:`salespyforce.core.Salesforce.get_api_versions` method
  to explicitly state what the method returns and its data type

Supporting Modules
------------------
Changes to the :doc:`supporting modules <supporting-modules>` are listed below.

* Completely refactored the :py:mod:`salespyforce.utils.version` module to retrieve the version
  from the package metadata and using it to define the ``__version__`` special variable
* Updated the ``HELPER_FILE_NAME`` value in the :py:mod:`salespyforce.utils.tests.resources` module
* Updated the following unit test modules to leverage the new pytest configuration:
    * :py:mod:`salespyforce.utils.tests.test_instantiate_object`
    * :py:mod:`salespyforce.utils.tests.test_sobjects`
    * :py:mod:`salespyforce.utils.tests.test_soql`
    * :py:mod:`salespyforce.utils.tests.test_sosl`
* Updated the :py:mod:`salespyforce.utils.log_utils` module to always define a default logging level
* Added a comment to skip assert checks by bandit in the modules used by pytest

General
-------
* Updated the Sphinx configuration (``docs/conf.py``) to follow recommendations and best practices
* Updated the ``pyproject.toml`` file to follow best practices and to include the following changes:
    * Changed the minimum supported Python version to be 3.9
    * Added hyperlinks to available resources and documentation
    * Added Trove classifiers for PyPI
    * Moved ``pytest`` to a dev dependency group
    * Removed ``setuptools`` and ``urllib3`` from runtime dependencies
    * Updated dependency versions to mitigate known vulnerabilities found in earlier versions
    * Added ``bandit`` with SARIF support to the dev dependencies
* Updated the ``requirements.txt`` file to be runtime-only and mirror the ``pyproject.toml`` file
* Replaced the ``.github/workflows/pythonpackage.yml`` workflow with ``.github/workflows/ci.yml``
  which has several improvements over the original file, including:
    * Dropping Python 3.6-3.8 and testing 3.9–3.12 on ``ubuntu-latest`` and ``macos-latest``
    * Using ``actions/checkout@v4`` and ``actions/setup-python@v5``
    * Installing Poetry via ``pipx`` and using ``poetry install --with dev``
    * Building wheel/sdist with ``poetry build``
    * Running Bandit only on Ubuntu (to save time)
    * Caching Poetry/pip downloads for speed
    * Removing the obsolete macOS target matrix
* Completely refactored the ``.github/scripts/encrypt_secret.sh`` script to add features and functionality
* Added a new helper file in ``.github/encrypted/`` for use with CI and unit testing with pytest
* Updated the ``.github/scripts/decrypt_helper.sh`` script to use the new helper file

Removed
=======

Core Object
-----------
Removals in the :doc:`core-object-methods` are listed below.

* Removed the hardcoded ``CURRENT_SFDC_VERSION`` constant in the :py:mod:`salespyforce.core.Salesforce` ``__init__``
  method as it is now obsolete

General
-------
* Removed ``.github/workflows/pythonpackage.yml`` (replaced by ``.github/workflows/ci.yml``)
* Removed the obsolete ``.github/encrypted/helper_shurt.yml.old.gpg`` helper file
* Removed the ``setup.py`` file as it is no longer needed for this package

|

-----

******
v1.3.0
******
**Release Date: 2025-11-11**

Added
=====

Core Object
-----------
Additions to the :doc:`core-object-methods` are listed below.

* Added the :py:meth:`salespyforce.core.Salesforce.Knowledge.archive_article` method
* Added the ``next_records_url`` parameter in the
  :py:meth:`salespyforce.core.Salesforce.soql_query` method and added the ability to
  query using a ``nextRecordsUrl`` value

Primary Modules
---------------
Additions to the :doc:`primary modules <primary-modules>` are listed below.

* Added the :py:func:`salespyforce.knowledge.archive_article` function

|

-----

******
v1.2.2
******
**Release Date: 2023-11-14**

Changed
=======

Core Object
-----------
Changes to the :doc:`core-object-methods` are listed below.

* Updated the :py:meth:`salespyforce.core.Salesforce.Knowledge.check_for_existing_article` method
  to specify whether archived articles will be included in the query results

Primary Modules
---------------
Changes to the :doc:`primary modules <primary-modules>` are listed below.

* Updated the :py:func:`salespyforce.knowledge.check_for_existing_article` function
  to specify whether archived articles will be included in the query results

|

-----

******
v1.2.1
******
**Release Date: 2023-09-01**

Changed
=======

Core Object
-----------
Changes to the :doc:`core-object-methods` are listed below.

* Changed the ``CURRENT_SFDC_VERSION`` value to be ``58.0``
* Updated the :py:meth:`salespyforce.core.Salesforce.Knowledge.publish_article` method to return a
  Boolean value indicating the successful outcome by default, while optionally being able to return
  the full API response

Primary Modules
---------------
Changes to the :doc:`primary modules <primary-modules>` are listed below.

* Updated the :py:func:`salespyforce.knowledge.publish_article` function to return a Boolean value
  indicating the successful outcome by default, while optionally being able to return the full
  API response

|

-----

******
v1.2.0
******
**Release Date: 2023-08-31**

Added
=====

Core Object
-----------
Additions to the :doc:`core-object-methods` are listed below.

* Added the :py:meth:`salespyforce.core.Salesforce.Knowledge.assign_data_category` method

Primary Modules
---------------
Additions to the :doc:`primary modules <primary-modules>` are listed below.

* Added the :py:func:`salespyforce.knowledge.assign_data_category` function


Changed
=======

Primary Modules
---------------
Changes to the :doc:`primary modules <primary-modules>` are listed below.

* Updated when Lightning URLs are defined and fixed an extraneous slash issue with
  the :py:func:`salespyforce.knowledge.get_article_url` function

|

-----

******
v1.1.2
******
**Release Date: 2023-06-05**

Changed
=======

General
-------
Only the version was changed in this release to address an issue with PyPI distribution.

|

-----

******
v1.1.1
******
**Release Date: 2023-06-05**

Changed
=======

General
-------
Only the version was changed in this release to address an issue with PyPI distribution.

|

-----

******
v1.1.0
******
**Release Date: 2023-05-29**

Added
=====

Core Object
-----------
Additions to the :doc:`core-object-methods` are listed below.

* Added the :py:meth:`salespyforce.core.Salesforce.get_org_limits` method
* Added the :py:meth:`salespyforce.core.Salesforce.search_string` method

Supporting Modules
------------------
Additions to the :doc:`supporting modules <supporting-modules>` are listed below.

* Added the :py:mod:`salespyforce.utils.tests.resources` module with the following functions and classes:
    * :py:class:`salespyforce.utils.tests.resources.MockResponse`
    * :py:func:`salespyforce.utils.tests.resources.mock_success_post`
    * :py:func:`salespyforce.utils.tests.resources.mock_error_post`
    * :py:func:`salespyforce.utils.tests.resources.mock_sosl_get`
    * :py:func:`salespyforce.utils.tests.resources.set_package_path`
    * :py:func:`salespyforce.utils.tests.resources.import_modules`
    * :py:func:`salespyforce.utils.tests.resources.secrets_helper_exists`
    * :py:func:`salespyforce.utils.tests.resources.local_helper_exists`
    * :py:func:`salespyforce.utils.tests.resources.get_core_object`
    * :py:func:`salespyforce.utils.tests.resources.instantiate_with_secrets_helper`
    * :py:func:`salespyforce.utils.tests.resources.instantiate_with_local_helper`
* Added the :py:mod:`salespyforce.utils.tests.test_instantiate_object` module with the following functions:
    * :py:func:`salespyforce.utils.tests.test_instantiate_object.test_instantiate_core_object`
    * :py:func:`salespyforce.utils.tests.test_instantiate_object.test_get_api_versions`
    * :py:func:`salespyforce.utils.tests.test_instantiate_object.test_get_rest_resources`
    * :py:func:`salespyforce.utils.tests.test_instantiate_object.test_get_org_limits`
* Added the :py:mod:`salespyforce.utils.tests.test_sobjects` module with the following functions:
    * :py:func:`salespyforce.utils.tests.test_sobjects.test_get_all_sobjects`
    * :py:func:`salespyforce.utils.tests.test_sobjects.test_get_and_describe_sobject`
    * :py:func:`salespyforce.utils.tests.test_sobjects.test_create_record`
* Added the :py:mod:`salespyforce.utils.tests.test_soql` module with the following functions:
    * :py:func:`salespyforce.utils.tests.test_soql.test_soql_query`
