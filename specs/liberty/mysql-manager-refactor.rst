..
   This work is licensed under a Creative Commons Attribution 3.0 Unported
   License.

   http://creativecommons.org/licenses/by/3.0/legalcode

======================
MySQL Manager Refactor
======================

There are a number of forks of MySQL that differ to varying degrees. This
blueprint proposes the creation of a class structure for MySQL-derived
datastores to avoid duplication of code for features and capabilities shared
in common.

It is expected that the lessons learned from this effort will be applicable to
future efforts to provide differentiation for systems such as MongoDB and
PostgreSQL.

https://blueprints.launchpad.net/trove/+spec/mysql-manager-refactor

Problem Description
===================

In recent years, there have been a number forks of MySQL with varying levels of
divergence from MySQL Community Edition (CE). Commonly used variants of MySQL
include Percona and MariaDB. Specialized versions specific to a variant also
exist, such as Galera for MariaDB or MySQL Cluster (NDB). Despite the
differences, there is a great deal shared among these variants. As such,
wholly separate datastore implementations of each would result in duplicated
code, leading to maintainability difficulties and potential confusion for
operators expecting common functionality to be treated the same across systems.

Openstack Trove would benefit from the refactoring of the MySQL manager with
more consistent support for MySQL-like systems, simplified code maintenance as
the variants evolve and the ability to provide differentiating features. New
variants could also be introduced with relative ease.


Proposed Change
===============

The existing MySQL datastore code is found in
``trove/guestagent/datastore/mysql``. This datastore already effectively
serves as a sort of superclass, with both the Percona and MySQL datastores
pointing to the same management code. MariaDB is supported if the underlying
MariaDB instance is treated as if it were MySQL.

The crux of this blueprint is to move the majority of the existing MySQL
manager code into a new set of abstract classes, with stub subclasses for
MySQL, Percona and MariaDB datastores inheriting from them.

Due to the recent reorganization of datastores into a directory structure based
on maturity, there are two alternatives that we have considered.

**Maturity-Agnostic**

The first alternative is for base, inherited code to be agnostic of maturity.
This would result in

* The creation of a ``trove/guestagent/datastore/base`` directory, that would
  contain a directory with abstract classes for each "base" system. For now,
  this would be only MySQL, but in the future could also include systems with
  a number of variants/forks such as PostgreSQL.
* The majority of the current MySQL datastore code moving to
  ``trove/guestagent/datastore/base/mysql`` , but the classes made abstract.
* The existing MySQL datastore classes remaining where they are, but largely
  replaced with stub implementations that inherit from the new base classes.

The resulting file and directory structure would change from::

     trove/guestagent/datastore/mysql/manager.py
     trove/guestagent/datastore/mysql/service.py

to::

     trove/guestagent/datastore/base/mysql/manager.py
     trove/guestagent/datastore/base/mysql/service.py
     trove/guestagent/datastore/mysql/manager.py
     trove/guestagent/datastore/mysql/service.py
     trove/guestagent/datastore/experimental/mariadb/manager.py
     trove/guestagent/datastore/experimental/mariadb/service.py
     trove/guestagent/datastore/experimental/percona/manager.py
     trove/guestagent/datastore/experimental/percona/service.py

The benefit of this approach is a clean separation of the abstract code common
to variants of a datastore and the datastore implementations themselves. A
drawback is that it fits somewhat awkwardly with our maturity-based
reorganization, especially if a future base system has only experimental
datastores as subclasses.

**Maturity-Aware**

The second alternative is for the base mysql code to reside in the current
mysql datastore directory. This would result in

* The creation of new base implementations for the manager and service
  modules in the ``trove/guestagent/datastore/mysql`` directory
* The creation of explicit datastores for Percona and MariaDB with
  implementation classes that inherit from base MySQL.

The resulting file and directory structure would change from::

     trove/guestagent/datastore/mysql/manager.py
     trove/guestagent/datastore/mysql/service.py

to::

     trove/guestagent/datastore/mysql/manager_base.py
     trove/guestagent/datastore/mysql/service_base.py
     trove/guestagent/datastore/mysql/manager.py
     trove/guestagent/datastore/mysql/service.py
     trove/guestagent/datastore/experimental/mariadb/manager.py
     trove/guestagent/datastore/experimental/mariadb/service.py
     trove/guestagent/datastore/experimental/percona/manager.py
     trove/guestagent/datastore/experimental/percona/service.py


This approach has the benefit of less potential confusion about the maturity
level of the base code. However, it is not as not as clean an organization:
MySQL CE is treated as both a base system and an implementing datastore.

In both cases, a pass through the MySQL manager code would be done to identify
methods that should be made abstract. These methods would then be brought
"down" into the subclasses.

This blueprint does *not* attempt to create optimized MariaDB or Percona
datastores, but rather to lay the groundwork for their creation.

**Strategy consolidation**

Currently not included in the scope of this refactor, but an important future
consideration, are the associated strategies that can also have differences
across variants. For example, it may make sense to bring some or all of the
logic from the replication strategy into the datastore subtree to provide
differentiation.


Configuration
-------------

Guest agent configuration options that point to fully qualified classnames,
e.g::

   datastore_registry_ext =
     mysql:trove.guestagent.datastore.mysql.manager.Manager,
     percona:trove.guestagent.datastore.mysql.manager.Manager

will need to point to the new class names, e.g::


   datastore_registry_ext =
     mysql:trove.guestagent.datastore.mysql.manager.Manager,
     percona:trove.guestagent.datastore.percona.manager.Manager,
     mariadb:trove.guestagent.datastore.experimental.mariadb.manager.Manager


Database
--------

Nothing expected, but confirm.

Python API
----------

None.


CLI (python-troveclient)
------------------------

None.


Public API
----------

None.

Public API Security
-------------------

None.

Internal API
------------

None.

Guest Agent
-----------

Behaviour should remain the same, but location of the code would change.

Alternatives
------------

Two alternatives are discussed in the main Proposed Change section.

Implementation
==============

Assignee(s)
-----------

Primary assignee:

Launchpad/IRC: atomic77

Email: atomic@tesora.com


Milestones
----------

Target Milestone for completion:

liberty-1

Work Items
----------

* Reorganize code

* Create stub implementations of Percona and MariaDB datastores that inherit
  from base MySQL classes.

* Review MySQL datastore implementation for initial candidates for abstract
  methods. Bring down and reimplement in each of the three datastore
  implementations.

* Write additional integration tests

Upgrade Implications
====================

As with any change to the layout of the source tree, care must be taken by the
operator to ensure that the updating of the code on the guest agent coincides
with the updating of configuration files. This would only be an issue for
operators that eventually want to leverage the new optimized managers for
Percona, MariaDB, etc. as the location of the MySQL CE manager would remain
backwards-compatible.

Dependencies
============

None.

Testing
=======

Additional tests should be added to ensure that subclassing is working
correctly e.g. ensure that some Percona-specific code is not running against
MySQL datastores, etc.


Documentation Impact
====================

The documentation should be updated to inform operators of the new locations of
datastore implementations that could be added to the guestagent configuration
file.


References
==========

A related blueprint is experimental-datastores [1] as this impacts the
organization of datastore implementations into directories based on maturity
level.

[1] https://blueprints.launchpad.net/trove/+spec/experimental-datastores
