..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

..


=========================
CouchDB Backup & Restore
=========================

Add support for CouchDB backup and restore functionality in Trove.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/couchdb-backup-restore

Problem Description
===================

CouchDB is one of the NoSQL databases that Trove supports.  While Trove
provides support for doing backups and restores, this functionality has not
been implemented for CouchDB.

Proposed Change
===============

The recommended method for doing full backups in CouchDB is to do a simple
filesystem copy of the data files [1]_. Since CouchDB does not officially
support incremental backups, this feature will not be implemented in this
release.

CouchDB is a document based database system where each database consist of
several documents and each document is a JSON structure. In CouchDB, each
document is associated with a revision number. Each database is stored as a
single .couch file which is an append-only file (Every time a change is made
to the document, it does not overwrite the existing document, instead it
creates a new document with an updated version number). This makes it easy
to do a full backup by simply copying this .couch file.

The following steps give a high level overview of the full backup and restore
process for CouchDB.

Backup process is explained as follows:

1. Locate the database files to be backed up. By default, the database files
   are located under /var/lib/couchdb directory (this location will be
   specified in the couchdb config file under /etc/couchdb directory). In
   CouchDB, each database is wholly contained in a single append-only file.
   This means that we can take a backup while its being written to.
2. Compress and/or encrypt the database files and stream it to Swift storage.

Restore process is explained as follows:

1. Stream and uncompress backup from storage to the database file directory
   (this location is specified in the /etc/couchdb config file)
2. Change ownership of the files to the CouchDB user and group


Configuration
-------------

The following configuration options will be updated with the corresponding
values for CouchDB:

   - backup namespace
   - restore namespace
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

The following commands will be functional for CouchDB after these changes:

   - backup-create
   - backup-delete
   - backup-list
   - create --backup


Internal API
------------

None

Guest Agent
-----------

The CouchDB guestagent will be modified to add support for full backup and
restore functionality. In addition, new strategies will also be added to
support these new features.

The following guestagent file will be modified:
  - trove/guestagent/datastore/experimental/couchdb/manager.py

and the following new strategy files will be added for CouchDB:
  - trove/guestagent/strategies/backup/experimental/couchdb_impl.py
  - trove/guestagent/strategies/restore/experimental/couchdb_impl.py


Alternatives
------------
Since CouchDB does not officially support incremental backups, an alternative
to doing this is to use the CouchDB replication interface. CouchDB's
replication interface supports master-master replication model and replicates
at the database level. It uses the REST API to trigger replication between
databases on a source and target systems. If the databases are not on the same
system, the source/target should be specified in a URI format:

http://<address>:<port>/<database name>

An example of a request for replicating database 'db1' from a local server to
a remote server on x.x.x.x server would be:

curl -X POST -d '{"source":"db1","target":"http://x.x.x.x:5984:db1"}' \
      http://localhost:5984/_replicate

When replication is enabled for a database from a source to target system, it
uses the document revision numbers to track differences and detect conflicts
and resolve it.


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

Mariam John (mariamj@us.ibm.com)

Milestones
----------

Mitaka

Work Items
----------

There will only be one work item for this feature. This includes implementing
the strategies for CouchDB backup and restore and make the necessary
guestagent changes. This will also include test-cases necessary to test the
new functionalities.


Upgrade Implications
====================

None

Dependencies
============

None

Testing
=======

* Add new test cases to test backup and restore functionality for CouchDB:

    - Add new unit tests to test the newly implemented functionality
    - Add a new CouchDB helper class to the existing integration-test framework.


Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.


References
==========
.. [1] Filesystem Backup: http://wiki.apache.org/couchdb/FilesystemBackups?action=show

Appendix
========

None
