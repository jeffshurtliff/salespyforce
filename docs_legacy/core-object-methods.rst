########################
SalesPyForce Core Object
########################
This section provides details around the core module and the methods used
within the core object for the **salespyforce** package, which are listed below.

* `Init Module (salespyforce)`_
* `Core Module (salespyforce.core)`_
    * `Core Functionality Subclasses (salespyforce.core.Salesforce)`_
        * `Chatter Subclass (salespyforce.core.Salesforce.Chatter)`_
        * `Knowledge Subclass (salespyforce.core.Salesforce.Knowledge)`_

|

**************************
Init Module (salespyforce)
**************************
This module (being the primary ``__init__.py`` file for the library) provides a
"jumping-off-point" to initialize the primary :py:class:`salespyforce.core.Salesforce` object.

.. automodule:: salespyforce
   :members: Salesforce
   :special-members: __init__

:doc:`Return to Top <core-object-methods>`

|

*******************************
Core Module (salespyforce.core)
*******************************
This module contains the core object and functions to establish the connection to the API
and leverage it to perform various actions.

.. automodule:: salespyforce.core
   :members:
   :special-members: __init__

:doc:`Return to Top <core-object-methods>`

|

Core Functionality Subclasses (salespyforce.core.Salesforce)
============================================================
These classes below are inner/nested classes within the core :py:class:`salespyforce.core.Salesforce` class.

.. note:: The classes themselves are *PascalCase* format and singular (e.g. ``Knowledge``, etc.) whereas
          the names used to call the inner class methods are all *lowercase* (or *snake_case*) and plural.
          (e.g. ``core_object.knowledge.check_for_existing_article()``, etc.)

|

Chatter Subclass (salespyforce.core.Salesforce.Chatter)
-------------------------------------------------------
.. autoclass:: salespyforce.core::Salesforce.Chatter
   :members:
   :noindex:

:doc:`Return to Top <core-object-methods>`

|

Knowledge Subclass (salespyforce.core.Salesforce.Knowledge)
-----------------------------------------------------------
.. autoclass:: salespyforce.core::Salesforce.Knowledge
   :members:
   :noindex:

:doc:`Return to Top <core-object-methods>`

|
