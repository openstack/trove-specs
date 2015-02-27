..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode
..

===============================
Apache CouchDB plugin for Trove
===============================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/couchdb-plugin-trove

Problem Description
===============================

The aim of this blueprint is to enable Trove to support a new datastore type -
Apache CouchDB v1.6.1 on Ubuntu and Fedora, in addition to the other NoSQL databases
supported by Trove.

Proposed Change
===============================
To add support for this new datastore, we need to implement the following:
- Add a new diskimage-builder element for Apache CouchDB on Ubuntu and Fedora
- Implement the various datastore features like::

    - Launch
    - Reboot
    - Terminate
    - Backup
    - Restore
    - Resize
    - Replication

Configuration
---------------
A new configuration group for CouchDB and the different configuration options specific
to CouchDB in /trove/common/cfg.py.

Some of the examples for the configuration options are::

    - tcp_ports
    - udp_ports
    - backup_strategy
    - mount_point
    - usage_timeout
    - volume_support
    - device_path

Database
------------
None

Public API
------------
None

Internal API
------------
None

Guest Agent
------------
This requires implementing the various datastore feature for Apache CouchDB like Launch, Reboot,
Terminate,Backup, Restore, Resize and Replication. This will include adding the following files
specific to Apache CouchDB under the guestagent/datastore module::

    - manager.py
    - service.py
    - system.py

In addition to this, there will also be a class under guestagent/strategies/backup to implement
the backup and restore features and another class under guestagent/strategies/replication to
implement the replication feature. CouchDB uses the replication interface to do backups hence we
will only be implementing full backups for this release.

These changes wont affect the behavior of the guestagent or its interaction with other components.


Implementation
===============================

Assignee(s)
-----------
- mariamj@us.ibm.com (Primary Assignee)
- Susan Malaika (CouchDB Contact)

Milestones
----------
Kilo

Dependencies
============
None

Testing
=======
- Add new unit tests for the CouchDB guestAgent
- Add integration tests for end-to-end feature testing::

    - create/delete instance
    - create/restore backups
    - replication

Documentation Impact
====================
None

References
==========
[1] http://guide.couchdb.org/draft
[2] http://guide.couchdb.org/draft/api.html
[3] http://guide.couchdb.org/draft/replication.html


