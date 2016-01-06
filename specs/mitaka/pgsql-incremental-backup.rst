..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

..


=========================================
PostgreSQL Incremental Backup and Restore
=========================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

Trove currently only supports full backup and restore with the PostgreSQL guest
agent.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/postgresql-incremental-backup



Problem Description
===================

Currently, backups in PostgreSQL are done with the ``pg_dump`` and
``pg_restore`` tools, which produce efficient, logical backups. Unfortunately,
they cannot be used as the basis for incremental backups or point-in-time
recovery.


Proposed Change
===============


PostgreSQL Logging
------------------

In contrast to MySQL, PostgreSQL uses the same foundation for recovery,
replication and incremental backups. Central to this is the write-ahead log
(WAL) [1]_. With each update to the database, a WAL entry is created. The WAL
contents are periodically checkpointed to the main data files in the database
directory and are eventually purged depending on the system configuration.

In the event of a system crash, recovery proceeds by replaying the contents of
the WAL since the last checkpoint. This same mechanism is used, in a
"continuous" sense, for replication, and up until a specific WAL entry, for
point-in-time recovery [2]_.

So in order to support incremental backup, two parts are required:

* A base backup, a snapshot of the filesystem contents of the pgsql data
  directory

* The WAL files written since the previous backup up to the desired point in
  time

Base Backups
~~~~~~~~~~~~

Base backups are taken with the ``pg_basebackup`` filesystem-level backup tool
[3]_. ``pg_basebackup`` creates a copy of the binary files in the PostgreSQL
cluster data directory and enough WAL segments to allow the database to be
brought back to a consistent state. Associated with each backup is a log
location, normally indicated by the WAL file name and the position inside the
file.


Point-in-time Recovery and WAL Archiving
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PostgreSQL can be made to support Trove's notion of incremental backup and
restore by bootstrapping the recovery system. To restore an incremental backup
from a previous backup, in PostgreSQL, is to replay the WAL entries to a
designated point in time -- all that is required is the most recent base
backup, and all WAL files that were written since.

During normal operation of the database, as WAL data is written and then
checkpointed to the data files, unneeded files are purged. PostgreSQL can also
be configured to automatically archive WAL files, which can then be used for
the purposes of point-in-time recovery.


PostgreSQL has two important configuration parameters that manage WAL archiving
and WAL retrieval for recovery: ``archive_command`` and ``recovery_command``.

The parameters allow a great deal of flexibility in how WAL files are handled
-- all that is required is that the command returns 0 only in the event that
the file was successfully transferred. A simple example::

    archive_command = 'test ! -f /mnt/arch/%f && cp %p /mnt/arch/%f'

The above command checks for the existence of the file in the archive directory
/mnt/arch (to avoid overwritting an existing file) and then copies it in.

Similarly, for recovery::

    restore_command = 'cp /mnt/arch/%f "%p"'

The above commands assume that ``/mnt/arch`` is accessible and, for recovery,
contains the appropriate WAL files.

In principle ``archive_command`` can be anything, with a few important caveats:

* The speed of the archive_command must be fast enough to keep up with the
  on-going generation of WAL files

* The restore command must be able to reverse whatever operation is applied
  to the WAL file on archive


Assuming that an appropriate mechanism to archive and retrieve the WAL files is
in place,  incremental backup and restore become simple operations: an
incremental "backup" is done by creating a restore point, using
``pg_start_backup('my_restore_pt')``, and the equivalent restore is done by
restarting the server with a ``recovery_target_name = 'my_restore_pt'`` in the
recovery.conf file.


Incremental Collection of WAL Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider the following series of WAL files that may be found in the PostgreSQL
WAL archive directory::

    $ ls -lh /mnt/wal_arch
    -rw------- 1 postgres postgres  16M Oct 27 19:11 000000010000000000000016
    -rw------- 1 postgres postgres  16M Oct 27 19:11 000000010000000000000017
    -rw------- 1 postgres postgres  16M Oct 27 19:12 000000010000000000000018
    -rw------- 1 postgres postgres  16M Oct 27 19:12 000000010000000000000019
    -rw------- 1 postgres postgres  16M Oct 27 19:12 00000001000000000000001A

The WAL entry stream can be visualized as::

    --------------------------------------------------------
    |   16   |    17    |   18   |    19    |    1A   | ...
    --------------------------------------------------------
         ^                  ^                    ^
        B1                  I1                   I2

Suppose that base backup B1 was taken at file 16 position 48, incremental
backup I1 at file 18 position 30, and incremental backup I2 at file 1A
position 20.

I1 would consist of WAL files 16 through 18: the entries after position 48 in
file 16, where B1 was taken, would be needed, along with the contents of file
18 up until position 30.

I2 would consist of WAL files 18 through 1A.

This approach has the benefit of being consistent with the current paradigm
used by Trove for incremental backup and restore. The main downside is that
WAL data must be archived in two stages: once by PostgreSQL, local to the
instances, and a second time by Trove, to object storage. This introduces more
complexity and increases storage requirements on the instance.


Configuration
-------------

The new incremental backup and restore strategies will need to be added.

Database
--------

None.


Public API
----------

None.


Public API Security
-------------------

None.


Python API
----------

None.


CLI (python-troveclient)
------------------------

After implementation, the following CLI commands will work::

    trove backup-create <inst> <inc_backup> --parent <backup_id>
    trove create <inst> .. --backup <inc_backup_id>



Internal API
------------

None.


Guest Agent
-----------

A new backup and restore strategy based on pg_basebackup will be added.


Alternatives
------------


Tighter Postgresql - Swift Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A simpler approach would be to bypass the two-stage archive process, and have
PostgreSQL automatically manage the WAL archiving process to and from object
storage. For example, the archive command could run the WAL file through a
fast compressor such as Snappy or LZOP, encrypt and then ship the file to
Swift directly, with an equivalent reverse procedure for recovery.

This has the benefit of being simpler to implement, as most log handling is
pushed down to PostgreSQL, but has the significant side-effect of introducing
a relatively continuous stream of WAL data from the PostgreSQL guest to Swift,
something potentially unexpected and not consistent with the approach to
incremental backups on other datastores.


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  atomic77


Milestones
----------

  mitaka-1

Work Items
----------

* pg_basebackup full backup

* incremental backup

* integration tests

Upgrade Implications
====================

Backups taken with the old PgDump strategy will not be compatible with this new
strategy.


Dependencies
============

Ability to create pgsql instances in the generic int-test framework.

Testing
=======

Int-tests for incremental backup currently do not exist in the new generic
int-test framework and will be added. Unit tests will be added as necessary.


Documentation Impact
====================

The documentation will need to be updated to reflect the new backup and restore
strategy.


References
==========


.. [1] http://www.postgresql.org/docs/9.4/static/wal-configuration.html

.. [2] http://www.postgresql.org/docs/9.4/static/continuous-archiving.html

.. [3] http://www.postgresql.org/docs/current/static/app-pgbasebackup.html

Appendix
========

N/A
