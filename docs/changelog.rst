##########
Change Log
##########
This page documents the additions, changes, fixes, deprecations and removals made in each release.

******
v1.1.0
******
**Release Date: TBD**

Added
=====

Supporting Modules
------------------
Additions to the :doc:`supporting modules <supporting-modules>`.

* Added the :py:mod:`salespyforce.utils.tests.resources` module with the following functions and classes:
    * :py:class:`salespyforce.utils.tests.resources.MockResponse`
    * :py:func:`salespyforce.utils.tests.resources.mock_success_post`
    * :py:func:`salespyforce.utils.tests.resources.mock_error_post`
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
* Added the :py:mod:`salespyforce.utils.tests.test_sobjects` module with the following functions:
    * :py:func:`salespyforce.utils.tests.test_sobjects.test_get_all_sobjects`
    * :py:func:`salespyforce.utils.tests.test_sobjects.test_get_and_describe_sobject`
* Added the :py:mod:`salespyforce.utils.tests.test_soql` module with the following functions:
    * :py:func:`salespyforce.utils.tests.test_soql.test_soql_query`
