..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


=================
Redis Replication
=================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Replication functionality needs to be added to the Redis datastore.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/redis-replication


Problem Description
===================

At present, only single instances of Redis can be created.  While useful,
having multiple slaves that replicate off of a designated master is also
desirable.  This functionality will be addressed in this spec.


Proposed Change
===============

Redis replication is a very simple to use (and configure) master-slave
replication.  It allows Redis slaves to be exact copies of master servers. [1]_

Replication
-----------

Redis replication has the following features:

- Asynchronous
- Multiple slaves
- Slave-of-slave
- Non-blocking initialization of slaves

To improve performance, persistence can be turned off on the master node.  This
however can lead to a loss of data if the system reboots and Redis starts
automatically.  For this reason, the master node will be required to have
persistence enabled.

Creating a Redis replication network is handled by the Redis SLAVEOF command.
A new instance (or set of instances) will be created and the SLAVEOF command
executed on each one.  Having Trove create a backup and restore it is not
necessary, as Redis has this capability built into the SLAVEOF command.  This
means that the Redis replication strategy will need to bypass the creation of a
backup to add to the snapshot info, and the taskmanager will need to be
modified to handle this case.

::

    Note: Redis replication could be enabled using the current backup/restore
    implementation, however once the slave restarts (or starts for the first
    time), it will automatically do a full resync, thus rendering the backup
    obsolete.  [1]_

Enough disk space must be available on the master node to allow Redis to
persist its data to storage.

::

    Note: Starting in version 2.8.18, Redis has the (experimental) ability to
    stream the backup directly to the slave.  Since this behaviour is still
    considered experimental (in version 3.0), a specific version of Redis will
    not be required - beyond being >= 2.8 - as the feature could be removed in
    a future release.  If it exists, however, it can be used by Redis to
    increase performance on systems with slow disks.  A configuration parameter
    will be provided to allow operators to turn this feature on.

The Redis configuration file on each slave will have the corresponding values
set so that subsequent starting of the database will maintain the slave status.
As part of the slave configuration, all slaves will also be set to read-only.
As with the MySQL implementation, slave-of-slave will not be allowed.  The
feature could be augmented to include this in the future.

The steps to create a replication network is as follows:

* Create the necessary configuration file.  This will have the following
  settings:

    - slaveof <master_ip> <master_port>
    - slave-read-only
    - repl-diskless-sync-delay (if more than one slave is specified)

* Create 'n' new slave instances with the correct configuration file

Detach Replica
--------------

The current API for detach-replica will need to be implemented.  No additions
to the API are anticipated.

Failover
--------

The current APIs for failover (both eject-replica-source and
promote-to-replica-source) will need to be implemented.  When ejecting the
current replica source, a slave needs to be chosen as the new one.  This will
be done by overriding the _most_current_replica() method and having it query
each slave and choose the one with the smallest value for
'master_last_io_seconds_ago.'  This, presumably, will be the one with the most
current data.


Configuration
-------------

The default values for the following config options will need to be updated:

* replication_strategy


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

Existing Python bindings are sufficient, and no changes are anticipated.

CLI (python-troveclient)
------------------------

Once these changes are implemented, the following Trove CLI
commands will now be fully functional with Redis:

    - create --replica_of <id> --replica_count <n>
    - eject-replica-source
    - promote-to-replica-source
    - detach-replica

Internal API
------------

None

Guest Agent
-----------


The following files will need to be added to the guest agent, where the
corresponding implementation will reside:

.. code-block:: bash

    guestagent/strategies/replication/experimental/redis_sync.py

The following existing files will be updated:

.. code-block:: bash

    guestagent/datastore/experimental/redis/manager.py
    guestagent/datastore/experimental/redis/service.py
    guestagent/datastore/experimental/redis/system.py

No backwards compatibility issues are anticipated.


Alternatives
------------

No alternative solutions are proposed at this time.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  peterstac


Milestones
----------

Target Milestone for completion:
  Liberty-2

Work Items
----------

- Create replication strategy for Redis.
- Implement API calls for detach_replica, promote_to_replica_source and
  eject_replica_source.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

No new tests are deemed to be required (beyond the requisite unit tests).  The
int-tests group for Redis will be modified to run replication-related commands
during integration test runs.


Documentation Impact
====================

Datastore specific documentation should be modified to indicate that
replication is now supported by Redis, along with the corresponding
detach/failover commands.


References
==========

.. [1] Redis Replication: http://redis.io/topics/replication

