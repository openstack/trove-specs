..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

..


===============
Move to oslo_db
===============

Replace the trove.db.sqlalchemy package with the oslo_db library.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/move-to-oslo-db

Problem Description
===================

The current code uses the outdated incubator package for database
connectivity. The old package has some bugs such as not handling concurrent
threads correctly. This is a good opportunity to migrate to the oslo_db
library, replacing the trove.db.sqlalchemy package.

A similar move has been done by other OS projects such as nova [1]_.

Proposed Change
===============

oslo_db is a library that handles the common database connection and controls.
Change the trove.db.sqlalchemy engine and session handling to use the oslo_db
library. This transparently handles connections and sessions, and protects
against mismanaged connections in Trove's threaded environment.

The only external effect will be the exposure of oslo_db configuration
options.

Configuration
-------------

Add the configuration options for oslo_db to the [database] section [2]_.

Database
--------

The database connection is the only change. Data models and queries are not
affected.

Public API
----------

N/A

Public API Security
-------------------

N/A

Python API
----------

N/A

CLI (python-troveclient)
------------------------

N/A

Internal API
------------

N/A

Guest Agent
-----------

N/A

Alternatives
------------

Determine the root cause of the database connection mismanagement [3]_.
Previous efforts were unsuccessful.

Implementation
==============

Remove the engine and session management code and replace it with a facade
from oslo_db.

Assignee(s)
-----------

Matthew Van Dijk

Milestones
----------

Mitaka-1

Work Items
----------

* A single task for code changes
* Update docs with the new configuration settings

Upgrade Implications
====================

N/A

Dependencies
============

oslo_db

Testing
=======

Do not break existing tests - especially the fake mode tests.

Documentation Impact
====================

Describe the config variables that are in the database section.

References
==========

.. [1] `Nova's migration commit <https://review.openstack.org/#/c/101901/>`_.
.. [2] `oslo_db configuration options <http://docs.openstack.org/developer/oslo.db/opts.html#database?>`_.
.. [3] `Associated bug on Launchpad <https://bugs.launchpad.net/trove/+bug/1481493>`_.

Appendix
========

None
