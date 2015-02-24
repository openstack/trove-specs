..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

==========================
MongoDB Backup and Restore
==========================

Despite the previous efforts, Trove still does not provide backup or restore
functionality for MongoDB. This blueprint aims to support backup and restore
for single instances.

https://blueprints.launchpad.net/trove/+spec/backups-single-instance-mongodb

There is also a previous blueprint that incorporated single-instance backup
[7]_.

Problem Description
===================

Backup and restore capability is important for eventually moving the MongoDB
datastore out of the "experimental" stage. MongoDB provides two utilities,
mongodump and mongorestore, which work with BSON-based files: efficient, binary
equivalents of the JSON data that MongoDB manages. These utilties will be used
to provide a standard backup and restore strategy for the MongoDB datastore,
equivalent to the MySQLDump strategy for MySQL-based datastores.


Proposed Change
===============

An initial simple backup and restore strategy for MongoDB will be implemented
using the default parameters to the mongodump and mongorestore utilities. For
compatibility, it will avoid the new features provided in 3.0 (backups with
oplogs) and avoid the options no longer supported in 3.0 (backups taken with
direct filesystem access to the database).

Configuration
-------------

The default values for backup_strategy, backup_namespace and restore_namespace
for MongoDB will change to point to the appropriate locations.


Database
--------

None.

Public API
----------

There are no changes to the existing API, but this blueprint enables the use of
the backup-create, backup-delete and backup-list CLI commands for MongoDB
datastores.

Public API Security
-------------------

None.

Python API
----------

None (empty section added after merging)

CLI (python-troveclient)
------------------------

None (empty section added after merging)

Internal API
------------

None.

Guest Agent
-----------

The MongoDB guest agent will be modified to support the new backup and restore
strategies.

It is currently unclear whether the MongoDB backup and restore tools directly
support streaming. There is an open JIRA ticket [5]_, and some unofficial
third-party tools exist to support streaming [6]_. This seems to contradict the
documentation [8]_ which suggests streaming is supported. If streaming can be
implemented and supported it will be used, otherwise backup and restore will
fall back to a two-stage process.

The backup procedure will use the mongodump command to connect directly to the
running MongoDB server and dump the contents of the database onto local
storage, or compressed and streamed on the fly, if supported. The backup will
be streamed to the container configured in the backup_swift_container
configuration option.

The restore procedure works in reverse, streaming and uncompressing the backup
from object storage back onto the guest, then using the mongorestore command to
restore the database, or streamed and uncompressed in-place, if the tools
support it.

The _perform_restore and create_backup methods are implemented in:
trove/guestagent/datastore/experimental/mongodb/manager.py

The backup and restore implementation will go in their respective strategy
folders: trove/guestagent/strategies/backup/experimental/mongo_impl.py
trove/guestagent/strategies/restore/experimental/mongo_impl.py



Alternatives
------------

As of version 3.0, MongoDB supports consistent, point-in-time snapshots with
the use of --oplog to the mongodump command for single-server deployments.
Operations committed after the start of the mongodump command are logged to a
separate file, and this file can be replayed with the --oplogReplay parameter
to mongorestore. As previous versions of MongoDB, and sharded installations do
not support this, it has been left as future work: a subclassed backup/restore
strategy could be easily implemented for MongoDB 3.0 guests.

In addition, the MongoDB documentation recommends filesystem snapshots as the
preferred way to do backups [1]_. This pushes the problem down to the storage
layer, and so is currently not implemented as a backup/restore strategy for any
datastores in Trove. A spec was previously proposed [2]_ [3]_, and discussed on
the mailing list [4]_ but has yet to be implemented.


Implementation
==============

Assignee(s)
-----------

Primary assignee: atomic77

Building on previous efforts of:

Ramashri Umale <rumale@ebaysf.com>, Viswa Vutharkar <vpvutharkar@ebaysf.com>

Milestones
----------

Target Milestone for completion:

liberty-1

Work Items
----------

- rebase of last patchset uploaded on Oct 14, 2014 to current upstream trove

- change backup/restore to operate on a running MongoDB, as MongoDB 3.0
  deprecates --journal and --dbpath for mongodump

- review existing test cases for gaps, implement as necessary


Upgrade Implications
====================

None.

Dependencies
============

None.

Testing
=======

Test cases used for testing backup/restore for MySQL will be adapted to run
against MongoDB.

Documentation Impact
====================

The documentation should reflect that MongoDB backup/restore is supported for
single instances.


References
==========

.. [1] http://docs.mongodb.org/manual/tutorial/backup-with-filesystem-snapshots/

.. [2] https://blueprints.launchpad.net/trove/+spec/volume-snapshot

.. [3] https://wiki.openstack.org/wiki/Trove/volume-data-snapshot-design

.. [4] http://lists.openstack.org/pipermail/openstack-dev/2014-April/032673.html

.. [5] https://jira.mongodb.org/browse/TOOLS-23

.. [6] https://github.com/timisbusy/dumpstr

.. [7] https://blueprints.launchpad.net/trove/+spec/single-instance-mongodb-ga

.. [8] http://docs.mongodb.org/manual/reference/program/mongodump/#bin.mongodump

