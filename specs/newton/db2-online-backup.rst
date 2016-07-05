..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


====================================
DB2 Full Online Backup and Restore
====================================

Currently in Trove, we support full offline backups for DB2 which is the
default backup mechanism for DB2. This enables users to take full backups of
DB2 databases when no applications are connected to or using these databases.
While useful for cases where this downtime is okay, it is not very useful in
a production type environment were applications are expected to be online all
the time. DB2 provides a way to do online backups and this spec outlines how
we can implement a full online backup mechanism in Trove.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/db2-online-backup


Problem Description
===================

There are two types of backups we can perform using DB2 - offline and online.
Offline backups require users and applications to be disconnected from the
databases thereby requiring a certain down time. Online backups on the other
hand, can be performed while users are still connected to databases. Trove
currently supports full offline backups for DB2. In this spec, we explain
how to enable full online backups for DB2 in Trove.


Proposed Change
===============

As mentioned above, the difference between offline and online backup is that
in the former case all applications must disconnect from the database while
in the latter, applications can still be connected to databases while backup
is being taken. In order to enable online backups, archive logging needs to
be enabled. This allows applications to use the database even while backups
are being taken. Any updates made to the database is recorded in the logs.

Logging is a mechanism where every updates to a database is recorded to
transaction logs (also called active logs) as the data is being modified.
There are 2 types of logging mechanism - circular and archive logging. By
default, circular logging is enabled which means that after the last active
log is filled, the first active log is overwritten. With circular logging
as the default logging mechanism, only offline backups can be taken.

Using archive logging, the logs are stored in sequence and as logs get full,
they are archived. Archive logging allows users to restore databases by roll
forwarding to a particular point in time or a point before failure. Hence,
users can restore a database from a backup image and roll forward to a
particular point using logs thus getting it to a consistent state. For an
introduction to archive logging, please refer [1] and for an overview of how
transactional logging works in DB2, please refer [2].

To enable full online backup for Trove, the following steps need to be taken:

1. Create a directory to store the backups and archive logs -
   /home/db2inst1/db2inst1/backup/ArchiveLogs
2. When a database is created, if online backups is configured for DB2(through
   the backup_strategy config property), then configure the following database
   configuration parameter: 'LOGARCHMETH1' to   point to a location where the
   archive logs can be stored using the command:

     db2 update database configuration for <db> using LOGARCHMETH1
     'DISK:/home/db2inst1/backup/ArchiveLogs'

   Setting this database configuration parameter enables archive logging and
   stores the archive logs in a location different from the primary/active
   logs.Once this change is made, a full offline backup needs to be taken
   before any connections can be made to the database (this is because the
   database goes into a 'BACKUP_PENDING' state when this configuration
   change is made).

     db2 backup database <db> to /home/db2inst1/db2inst1/backup

   This backup can be deleted from the backup directory after this operation.
3. The online backup strategy for DB2 will comprise of the following actions:
    - Check if archive logging is enabled for each database
    - Check if there is enough space to store backups (which will include
      database and archived logs). The get_dbsize_info function that DB2
      provides can be used to get the size of the database directory. We can
      query the SYSIBMADM.LOG_UTILIZATION table to get the log space used for
      each database.
    - Do an online backup of the database and include the archive logs along
      with the backup image itself:

         db2 backup database <db> ONLINE to
         /home/db2inst1/db2inst1/backup INCLUDE LOGS

4. Once the backup is complete, compress/encrypt the backup inside the volume
   storage.
5. The compressed/encrypted file can then be stored in Swift under the
   database_backups container.
6. Once the backups are stored in Swift, we can go ahead and delete the backup
   files and archive logs from the backup directory.

Restoring a database includes restoring from an online backup image and
rolling forward the logs to the end of the backup to make sure the database is
in a consistent state.

1. Create a directory where the backup files and archive logs can be stored
2. Retrieve the backup from storage to the proper location
3. Use the following commands to restore the database and ensure it is in a
   consistent state:
   - db2 RESTORE DATABASE <db> FROM <backup_dir> LOGTARGET <log_dir>

    The above command restores the database from the specified online backup
    directory and extracts the archive log files into the log_dir

   - db2 ROLLFORWARD DATABASE <db> TO END OF BACKLOG AND COMPLETE

    This command will roll forward the restored database to a consistent state
    by applying the archive logs. To see more details on the ROLLFORWARD
    command, please refer [3].

Configuration
-------------

The default configuration values of the following will need to change to
correspond to the respective DB2 locations.

* backup_strategy
* backup_namespace
* restore_namespace

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

The DB2 guestagent will be modified to add support for full online backup
and restore functionality. In addition, new strategies will also be added
to support these new features.

The following guestagent files will be modified:
  - trove/guestagent/datastore/experimental/db2/service.py
  - trove/guestagent/datastore/experimental/db2/system.py

and the following new strategy files will be modified to add a new class
for online backups:

  - trove/guestagent/strategies/backup/experimental/db2_impl.py
  - trove/guestagent/strategies/restore/experimental/db2_impl.py

New classes will be added for online backup strategy and the existing
class needs to be renamed from DB2Backup -> DB2OfflineBackup

Alternatives
------------

None


Dashboard Impact (UX)
=====================

None


Implementation
==============

Assignee(s)
-----------

Mariam John (johnma)


Milestones
----------

Newton

Work Items
----------

There will only be one work item for this feature. This includes implementing
the strategies for DB2 online backup and restore and make the necessary
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

* Add new test cases to test online backup and restore functionality for DB2:

    - Add new unit tests to test the newly implemented functionality
    - Add a new DB2 helper class to the existing integration-test framework.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] https://www.ibm.com/support/knowledgecenter/SSEPGG_10.5.0/com.ibm.db2.luw.admin.ha.doc/doc/c0051344.html

.. [2] http://www.ibm.com/developerworks/data/library/techarticle/0301kline/0301kline.html

.. [3] https://www.ibm.com/support/knowledgecenter/SSEPGG_10.5.0/com.ibm.db2.luw.admin.cmd.doc/doc/r0001978.html


Appendix
========

None