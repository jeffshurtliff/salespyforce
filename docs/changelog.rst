##########
Change Log
##########
This page documents the additions, changes, fixes, deprecations and removals made in each release.

******
v1.2.1
******
**Release Date: TBD**

Changed
=======

Core Object
-----------
Changes to the :doc:`core-object-methods`.

* Changed the ``CURRENT_SFDC_VERSION`` value to be ``58.0``.
* Updated the :py:meth:`salespyforce.core.Salesforce.Knowledge.publish_article` method to return a
  Boolean value indicating the successful outcome by default, while optionally being able to return
  the full API response.

Primary Modules
---------------
Changes to the :doc:`primary modules <primary-modules>`.

* Updated the :py:func:`salespyforce.knowledge.publish_article` function to return a Boolean value
  indicating the successful outcome by default, while optionally being able to return the full
  API response.

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
Additions to the :doc:`core-object-methods`.

* Added the :py:meth:`salespyforce.core.Salesforce.Knowledge.assign_data_category` method.

Primary Modules
---------------
Additions to the :doc:`primary modules <primary-modules>`.

* Added the :py:func:`salespyforce.knowledge.assign_data_category` function.


Changed
=======

Primary Modules
---------------
Changes to the :doc:`primary modules <primary-modules>`.

* Updated when Lightning URLs are defined and fixed an extraneous slash issue with
  the :py:func:`salespyforce.knowledge.get_article_url` function.

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
Additions to the :doc:`core-object-methods`.

* Added the :py:meth:`salespyforce.core.Salesforce.get_org_limits` method.
* Added the :py:meth:`salespyforce.core.Salesforce.search_string` method.

Supporting Modules
------------------
Additions to the :doc:`supporting modules <supporting-modules>`.

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
