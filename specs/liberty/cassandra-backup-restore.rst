..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

==========================
Cassandra Backup & Restore
==========================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/cassandra-backup-restore

Problem Description
===================

The Cassandra datastore currently does not support any backup/restore strategy.

Proposed Change
===============

The patch set will implement full backup/restore of a single instance
using the Nodetool [1]_ utility for Cassandra 2.1 [3]_.

Configuration
-------------

The following Cassandra configuration options will be updated:
   - backup/restore namespaces
   - backup_strategy

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

The following Trove CLI commands (upon completion)
will be fully functional with Cassandra:

   - backup-create
   - backup-delete
   - backup-list
   - create --backup

Internal API
------------

None

Guest Agent
-----------

We are implementing full backup using node snapshots following the procedure
outlined in the Nodetool manual [2]_.
Nodetool can take a snapshot of one or more keyspace(s).
A snapshot can be restored by moving all *\*.db* files from a snapshot
directory to the respective keyspace overwriting any existing files.

When a snapshot is taken Cassandra starts saving all changes into new
data files keeping the old ones at the same state as when the snapshot was
taken.
The data storage must have enough capacity to accommodate the backlog of all
changes throughout the duration of the backup operation until the snapshots get
cleaned up.

Backups are streamed to and from a remote storage as (TAR) archives.
We now outline the general procedure for creating and restoring
such an archive.

Unique backup IDs will be used for snapshot names, to avoid collisions between
concurrent backups.

The Backup Procedure:

0. Make sure the database is up an running.

1. Clear any existing snapshots (nodetool clearsnapshot) with the same name
   as the created one.

2. Take a snapshot of all keyspaces (nodetool snapshot).

3. Collect all *\*.db* files from the snapshot directories.

4. Package the snapshot files into a single TAR archive
   (compressing and/or encrypting as required) while streaming
   the output to Swift storage under the database_backups container.

   Transform the paths such that the backup can be restored simply by
   extracting the archive right to an existing data directory.
   This is to ensure we can always restore an old backup
   even if the standard guest agent data directory changes.

5. Clear the created snapshots as in (1).

The Restore Procedure:

0. Stop the database if running and clear any files generated in the system
   keyspace.

1. Create a new data directory.

2. Read backup from storage unpacking it to the data directory.

3. Update ownership of the restored files to the Cassandra user.

Additional Considerations:

Instances are created as single-node clusters. A restored instance
should therefore belong to its own cluster as well.
The original cluster name property has to be reset to match the new unique ID
of the restored instance. This is to ensure that the restored instance is a
part of a new single-node cluster rather than forming a one with the
original node or other instances restored from the same backup.
Cluster name is stored in the database and is required to match the
configuration value. Cassandra fails to start otherwise.

A general 'cluster_name' reset procedure is:

1. Update the name in the system keyspace table.

2. Update the name in the configuration file.

3. Restart the service.

The 'superuser' *("root")* password stored in the system keyspace
needs to be reset before we can start up with restored data.

A general password reset procedure is:

1. Disable user authentication and remote access.

2. Restart the service.

3. Update the password in the 'system_auth.credentials' table.

4. Re-enable authentication and make the host reachable.

5. Restart the service.

Alternatives
------------

None

Implementation
==============

Assignee(s)
-----------

Petr Malik <pmalik@tesora.com>

Milestones
----------

Liberty-1

Work Items
----------

1. Implement functionality needed for resetting cluster name and superuser
   password.
2. Implement backup/restore API calls.

Upgrade Implications
====================

None

Dependencies
============

The patch set will be building on functionality implemented in blueprints:
cassandra-database-user-functions [4]_ and cassandra-configuration-groups [5]_

Testing
=======

Unittests will be added to validate implemented functions and non-trivial
codepaths. We do not implement functional tests as a part of this patch set.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.
Also note the new configuration options - backup/restore namespaces and
backup_strategy for Cassandra datastore.

References
==========

.. [1] Documentation on Nodetool utility for Cassandra 2.1: http://docs.datastax.com/en/cassandra/2.1/cassandra/tools/toolsNodetool_r.html
.. [2] Manual on Backup and Restore for Cassandra 2.1: http://docs.datastax.com/en/cassandra/2.1/cassandra/operations/ops_backup_restore_c.html
.. [3] Documentation on Cassandra 2.1: http://docs.datastax.com/en/cassandra/2.1/cassandra/gettingStartedCassandraIntro.html
.. [4] Database and User Functions for Cassandra: https://blueprints.launchpad.net/trove/+spec/cassandra-database-user-functions
.. [5] Configuration Groups for Cassandra: https://blueprints.launchpad.net/trove/+spec/cassandra-configuration-groups
