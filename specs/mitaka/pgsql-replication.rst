..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

======================
PostgreSQL Replication
======================

From version 9.0 onwards, PostgreSQL ships with streaming replication as part
of the core product, reversing a long held policy of leaving replication to
third-party add-ons such as Slony or pgpool.

This blueprint proposes to support streaming replication since it is shipped
with the core product, although a discussion of some of the other PostgreSQL
options can be found in the alternatives section.

https://blueprints.launchpad.net/trove/+spec/postgresql-replication


Problem Description
===================

In order to achieve feature parity with MySQL, Trove should provide support for
at least one of the replication solutions for PostgreSQL.


Proposed Change
===============

Configuration
-------------

The standard parameters for enabling replication strategies,
``replication_strategy`` and ``replication_namespace``, will be added to point
to the strategy code for PostgreSQL guests.


Database
--------

None.

Public API
----------

As with other datastores that support replication, the create instance
operation will support the ``replica_of`` and ``replica_count`` fields for
PostgreSQL guests::

    POST http://127.0.0.1:8779/v1.0/<tenant id>/instances
    {
        "instance": {
            "volume": {"size": <size>},
            "flavorRef": "<flavor-id>",
            "name": "s",
            "replica_of": "<master id>",
            *"replica_count": "<n>"*
        }
    }


For guests with ``pg_rewind`` [9]_ support, the following instance actions are
supported::

    POST http://127.0.0.1:8779/v1.0/<tenant id>/instance/<instance id>/action
    {
        *"detach_replica": null*
    }

    POST http://127.0.0.1:8779/v1.0/<tenant id>/instance/<instance id>/action
    {
        *"eject_replica_source": null*
    }

    POST http://127.0.0.1:8779/v1.0/<tenant id>/instance/<instance id>/action
    {
        *"promote_to_replica_source": null*
    }


Public API Security
-------------------

None.

Python API
----------

None.

CLI (python-troveclient)
------------------------

As with other datastores that support replication, this will enable the
commands::

    trove create <inst> .. --replica_of <master_inst>

on PostgreSQL guests. With ``pg_rewind`` [9]_ support on the guest, failover
and reconfiguration commands are supported::

    trove detach-replica <inst>
    trove eject-replica-source <inst>
    trove promote-to-replica-source <inst>


Internal API
------------

None.

Guest Agent
-----------

Write-Ahead Log (WAL) and Continuous Shipping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PostgreSQL provides both high performance and crash recovery capability through
the use of a write-ahead log. The WAL files are appended to for every change
to the database, with periodic checkpoints to purge the logs and integrate the
changes into the database files [4]_.

PostgreSQL streaming replication is built on top of the recovery system: a
master database operates in continuous archiving mode, sending the contents of
its WAL files to one or more slave servers. These slave servers, in turn,
operate in continuous recovery mode, "recovering" from the logs as they are
received. A slave can be promoted in place of a failed master, and can be
configured to support read-only transactions while in recovery mode.


Replication interface
~~~~~~~~~~~~~~~~~~~~~



Replication Snapshots
'''''''''''''''''''''

The PostgreSQL guestagent currently provides a backup and restore strategy
which makes use of the ``pg_dump`` and ``pg_restore`` commands. These produce
logical dumps which cannot be used as part of a replication system that
depends on continuous archiving. As such, a backup/restore strategy using the
``pg_basebackup`` tool is a requirement for replication.


Enabling a master
'''''''''''''''''

In order to support hot standby slaves, a PostgreSQL master must have
``wal_level`` set to hot_standby, which is the most verbose mode. Replication
is handled through the use of a user that has been given REPLICATION privilege
[6]_ and has been explicitly allowed to access the special replication
database in the pg_hba.conf file. After enabling these changes, a
configuration reload is done.

Enabling a slave
''''''''''''''''

Enabling a slave requires a recent backup to be restored. Since streaming
replication bootstraps the recovery system, a recovery.conf file is written to
the ``PGDATA`` directory containing the connection details for the master that
should be replicated from. A restart is required to enable continuous recovery
mode.


Detaching a slave
'''''''''''''''''

To detach a slave in PostgreSQL means to stop recovery mode. This is done by
writing a special trigger file, configured with the ``trigger_file`` option in
the recovery configuration.


Demote master
'''''''''''''

To demote a master requires no special action other than to revert
configuration changes to their defaults.

Failover and Failback
~~~~~~~~~~~~~~~~~~~~~

The failover process in Trove is controlled by the task-manager, but the guest
agent must implement functions that allow the task manager to determine the
best slave to promote and when it can proceed.


Global Transactions
'''''''''''''''''''

Standard PostgreSQL does not support an equivalent of the GTID in MySQL, so the
combination of host + WAL location [8]_ will be used as a transaction
identifier where necessary.

A simple polling mechanism will be implemented to determine when a slave has
caught up to the point of a particular change.

Reattaching Slaves
''''''''''''''''''
Failback in postgresql is complicated by recovery timelines [2]_ . When a slave
is triggered out of recovery mode, it jumps to a new timeline, generating new
WAL data into a "fork" of the previous database state. This can be seen in the
example of these 24-character WAL filenames::

    000000010000000000000006
    000000020000000000000007

These represent WAL files 6 and 7, but the 7th file is on a second timeline
forked from the first.

When a master is demoted, however, it does not change timelines, and so in
order to safely reattach this demoted master to a newly-promoted slave, a
timeline resync is required.

This can only be done safely through the use of the tool pg_rewind [9]_. This
tool is supported for PostgreSQL 9.4, but must be compiled separately. In
PostgreSQL 9.5 it will be shipped with the core product.

For guests that have pg_rewind available, failback can be done, otherwise a
manual recreate of another slave from the master is required.


Alternatives
------------

A number of third-party replication options exist for PostgreSQL, including
Slony, pgpool-II and a number of commercially-available solutions [1]_.

pgpool-II depends on middleware that inserts itself between the client and the
underlying database instances. It provides the benefit of multi-master
replication, however conflict-resolution may be required in some cases.

Slony provides master-slave replication using table-level triggers. It has
greater overhead on the master database than standard streaming replication,
but has the benefit of table-level granularity.


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

Primary assignee: atomic77

Milestones
----------

Target Milestone for completion:

mitaka-1

Work Items
----------

* implement basic streaming replication

* implement failover-related APIs

* add postgresql-specific hooks as necessary to enable generic int-tests for
  replication to run against PostgreSQL guests


Upgrade Implications
====================

None.

Dependencies
============

pg_basebackup incremental backup and restore strategy for PostgreSQL. [10]_

Testing
=======

Postgresql-specific hooks to the generic int-test framework will be added as
necessary.


Documentation Impact
====================

The documentation will need to be updated to indicate that the PostgreSQL guest
supports replication.

Appendix
========

None.

References
==========

.. [1] http://www.postgresql.org/docs/9.4/static/different-replication-solutions.html

.. [2] http://www.postgresql.org/docs/9.4/static/continuous-archiving.html

.. [3] http://www.postgresql.org/docs/current/static/app-pgbasebackup.html

.. [4] http://www.postgresql.org/docs/9.0/static/wal-configuration.html

.. [5] http://www.postgresql.org/docs/9.4/static/warm-standby-failover.html

.. [6] http://www.postgresql.org/docs/current/static/sql-createrole.html

.. [7] http://www.postgresql.org/message-id/flat/CA+TgmobWQJ-GCa_tWUc4=80A
       1RJ2_+Rq3w_MqaVguk_q018dqw@mail.gmail.com#CA+TgmobWQJ-GCa_tWUc4=80A1RJ
       2_+Rq3w_MqaVguk_q018dqw@mail.gmail.com

.. [8] By "WAL location" we mean the position in the WAL file, as would be
       returned by the ``pg_current_xlog_location()`` system
       administration function

.. [9] https://github.com/vmware/pg_rewind/tree/REL9_4_STABLE

.. [10] https://blueprints.launchpad.net/trove/+spec/postgresql-incremental-backup
