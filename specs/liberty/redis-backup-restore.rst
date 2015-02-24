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


========================
Redis Backup And Restore
========================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Backup and Restore functionality needs to be added to the Redis datastore.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/redis-backup-restore


Problem Description
===================

Trove instances created with the Redis datastore do not currently have a way to
create a backup or to restore from one.  This functionality needs to be added.


Proposed Change
===============

Redis currently has two persistence strategies: RDB [*]_ and AOF [*]_ (both can
be used concurrently).  The backup strategy is the same for both, however
restoring is a little different if AOF is enabled (whether or not RDB is also
enabled).

Note: All necessary changes are anticipated to be made in the Trove guestagent
 code.

.. [*] Redis DataBase
.. [*] Append-Only File

Backup
------

The redis-cli utility will be used to create the backup.  This process is the
same regardless of the persistence strategy configured within Redis.  The
process will be as follows [1]_:

* Determine the directory where the backup files are written.  This directory
  is stored in the redis configuration file (typically /etc/redis/redis.conf)
  under the dir keyword.  At present this location is hard-coded in the redis
  config.template file, however it could be exposed in the future through
  configuration groups.
* Find the time of the last Redis persistence run, and retain the information
  temporarily.  This is accomplished by executing the LASTSAVE command through
  the redis-cli, and is necessary to determine when the next run completes (as
  explained below).
* Start a backup using the redis-cli utility.  This is done by executing the
  BGSAVE command. [2]_  Note: If Redis persistence is turned off
  (it is on by default in the config.template) then enough disk space
  must be available to write the backup file.
* Wait until the backup completes.  This is determined by polling using the
  LASTSAVE command as above, and waiting until the timestamp changes. [3]_
* Compress/encrypt the backup
* Stream the compressed/encrypted output to storage in Swift under the
  database_backups container.  If persistence is turned off, the backup
  file can then be deleted.

Restore
-------

Restoring a Redis server from backup depends on the persistence method that is
running on the server. [4]_

To restore a Redis server from a backup [1]_:

* Determine if AOF mode is enabled

If AOF is disabled:

* Determine the location where backup files are located
* Make sure the redis server is not running (stop if necessary)
* Remove the existing dump.rdb file
* Retrieve the backup from storage
* Put the backup into the proper location
* Change the ownership to redis:redis
* Start the redis server

If AOF is enabled:

* Determine the location where backup files are located
* Make sure the redis server is not running (stop if necessary)
* Remove existing dump.rdb and appendonly.aof
* Retrieve the backup from storage
* Put the backup into the proper location
* Change the ownership to redis:redis
* Disable AOF in the Redis configuration
* Start the redis server
* Create a new AOF file
* Stop the Redis server
* Turn on AOF in the Redis configuration
* Start the Redis server


Configuration
-------------

The default values for the following config options will need to be updated:

* backup_namespace
* restore_namespace
* backup_strategy


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

    - backup-create
    - backup-delete
    - backup-list
    - backup-list-instance
    - backup-show
    - create --backup

Internal API
------------

None

Guest Agent
-----------


The following files will need to be added to the guest agent, where the
corresponding implementation will reside:

.. code-block:: bash

    guestagent/strategies/backup/experimental/redis_impl.py
    guestagent/strategies/restore/experimental/redis_impl.py

The following existing files will be updated:

.. code-block:: bash

    guestagent/datastore/experimental/redis/manager.py

No backwards compatibility issues are anticipated.


Alternatives
------------

None


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  peterstac


Milestones
----------

Target Milestone for completion:
  Liberty-1

Work Items
----------

The API calls for backup and restore need to be implemented.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

No new tests are deemed to be required (beyond the requisite unit tests).  The
int-tests group for Redis will be modified to run backup-related commands
during integration test runs.  It would be good if a 3rd party Redis CI could
be set up to test Redis integration functionality, but at present this is not
available.


Documentation Impact
====================

Datastore specific documentation should be modified to indicate that backup and
restore of a Redis Trove instance is now supported.


References
==========

.. [1] Backup and Restore procedure: http://zdk.blinkenshell.org/redis-backup-and-restore
.. [2] Create Redis Backup: http://redis.io/commands/bgsave
.. [3] How to tell when a Backup is finished: http://redis.io/commands/lastsave
.. [4] Redis Persistence: http://redis.io/topics/persistence
