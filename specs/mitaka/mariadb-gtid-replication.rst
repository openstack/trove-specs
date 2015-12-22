..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


=====================================
Add MariaDB GTID Replication Strategy
=====================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::


Global Transaction ID (GTID) Replication support was added during
the Kilo release for MySQL 5.6 and later. The equivalent for MySQL 5.6,
MariaDB 10, has a different implementation of GTID. By creating a similar
strategy implementation we could get support for GTID Replication for the
MariaDB 10 datastore.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/mariadb-gtid-replication

Problem Description
===================

In order to create a replica of a MariaDB instance you can only use
binary logs based replication. GTID replication was added as an alternative
for replication for MySQL 5.6, but it's not available
for the equivalent for it, MariaDB 10.

Proposed Change
===============

We would need to create
trove/trove/guestagent/strategies/replication/experimental/mariadb_gtid.py
in order to support replication for MariaDB.

The SQL issued to set a new empty slave server and replicate all of the
master's binlog from the start is as follows [2]_:

.. code-block:: sql

    CHANGE MASTER TO master_host="%(host)s", master_port=%(port)s, \
    master_user="%(user)s", master_password="%(password)s", \
    master_use_gtid=current_pos;
    START SLAVE;


By default, the GTID position for a newly installed server is empty,
which makes the slave replicate from the start of the master's binlogs. [3]_
current_pos in the SQL query carries that position.

It doesn't differ too much on what is being done for MySQL [1]_,
but doing a refactoring might not be the best call right now since
it would add unnecessary complexity to the existing strategy.

Configuration
-------------

None

Database
--------

None

Public API
----------

None

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

None

Internal API
------------

None

Guest Agent
-----------

None

Alternatives
------------

Don't support GTID-based Replication for MariaDB.


Dashboard Impact (UX)
=====================

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vkmc
  vgnbkr

Milestones
----------

Target Milestone for completion:
  Mitaka-2

Work Items
----------

* Create MariaDB GTID Replication strategy
* Create integration tests for replication in MariaDB 10

Upgrade Implications
====================

None

Dependencies
============

None

Testing
=======

Integration tests will be added to cover this functionality.

Documentation Impact
====================

Docs explaining this new addition will be added.

References
==========

.. [1] https://github.com/openstack/trove/blob/master/trove/guestagent/strategies/replication/mysql_gtid.py

.. [2] https://mariadb.com/kb/en/mariadb/gtid/

.. [3] https://mariadb.com/kb/en/mariadb/gtid/

Appendix
========

None
