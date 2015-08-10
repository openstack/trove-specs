..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode


=========================
MariaDB Datastore Support
=========================

MariaDB [1]_ is a community-developed fork of MySQL licensed under GNU GPL.

It aims to maintain high compatibility with MySQL, ensuring a "drop-in"
replacement capability with library binary equivalency and exact matching
with MySQL APIs and commands.

https://blueprints.launchpad.net/trove/+spec/mariadb-datastore-support

Problem Description
===================

MariaDB versioning follow the MySQL's versioning scheme up to version 5.5.
Thus, MariaDB 5.5 offers all of the MySQL 5.5 features. After the 5.5 version,
MariaDB developers decided to start a branch numbered 10, as an attempt
to make it clear that specific new features have been developed in MariaDB 10
that are not included in MySQL 5.6.

Currently, Trove has support for MySQL but not for MariaDB in particular.
This could be easily fixed for MariaDB 5.5 by just adapting the main
configuration file (my.cnf).
But in the case of MariaDB 10, this will no-longer be so straightforward.

With this in mind, and the fact that several GNU/Linux distributions
are adopting MariaDB as the default MySQL implementation, it seems important
to add support for this datastore.

Proposed Change
===============

To add support for this datastore, we will need the following:

 - Implement instance management for the datastore:

  - Launch new instance
  - Terminate instance
  - Reboot instance
  - Resize instance

 - Implement user and database management for the datastore:

  - CRUD users
  - CRUD databases

 - Add new elements in trove-integration project to enable the creation
   of Ubuntu/Fedora images with MariaDB

In this first approach, it makes sense to take profit of the MySQL Refactor
spec [2]_ and inherit as much as possible from the MySQL implementation,
providing a cleaner way to launch MariaDB 5.5 instances.

In a follow up spec, differences in implementation will be tackled
(e.g. a GTID based replication strategy [3]_ for MariaDB 10 will be proposed)
and we would be able to provide support for MariaDB newer versions.

Configuration
-------------

A new configuration group for MariaDB and the different configuration options
specific to MariaDB have to be added to trove/common/cfg.py

Some of the examples for the configuration options are:

 - tcp_ports
 - udp_ports
 - backup_strategy
 - backup_incremental_strategy
 - replication_strategy
 - mount_point
 - volume_support
 - device_path
 - backup_namespace
 - restore_namespace

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

- This requires implementing the various datastore features for MariaDB
  like Launch, Reboot, Terminate and Resize.

- This requires implementing the various CRUD features for users and databases
  for MariaDB.

- This will include adding the following files specific to MariaDB under the
  guestagent/datastore module:

 - manager.py
 - service.py

These changes will not affect the behavior of the guestagent or its interaction
with other components.

Alternatives
------------

Do not support MariaDB.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  - vkmc

Milestones
----------

Liberty-3

Work Items
----------

- Update trove-integration to support MariaDB image creation

  - Create MariaDB elements for Ubuntu/Fedora

- Update trove/common/cfg.py with the configuration options for MariaDB
- Add MariaDB configuration templates under templates/mariadb
- Add support for instance management features in
  guestagent/experimental/mariadb/service.py [*]
- Add support for user and databases management features in
  guestagent/experimental/mariadb/service.py [*]

- Add unit and integration tests specific to MariaDB

[*] This items rely on the MySQL Manager Refactor spec [2]_ and in the first
iteration it will only require inheriting from the MySQL existing
implementation.

Upgrade Implications
====================

None

Dependencies
============

MySQL Manager Refactor [2]_

Testing
=======

- Unit tests will be added for MariaDB guestagent

- Integration tests will be added for end-to-end feature testing

 - Create/Delete MariaDB instances
 - Resize MariaDB instances

Documentation Impact
====================

- Docs will be updated to indicate that:

 - Which MariaDB version is supported
 - Trove capabilities for MariaDB datastore
 - Instructions to build guest MariaDB images using trove-integration elements

References
==========

.. [1] https://mariadb.org/

.. [2] http://specs.openstack.org/openstack/trove-specs/specs/liberty/mysql-manager-refactor.html

.. [3] https://mariadb.com/kb/en/mariadb/global-transaction-id/
