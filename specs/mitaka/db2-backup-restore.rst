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


======================
DB2 Backup And Restore
======================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

The DB2 Express C datastore in Trove lacks backup and restore functionality
at the moment. This blueprint aims at adding the feature of backup and
restore to DB2 in Trove.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/db2-backup-restore


Problem Description
===================

Currently, there is no way to create backups of DB2 databases using Trove nor
is it possible to perform a restore from a backup. Since this functionality
is core to a data model and typical use case, it is imperative for Trove to
add it.


Proposed Change
===============

The simplest form of database backup and restore will be implemented for DB2
creating a backup image in a default location. Since by default, DB2
databases are in a circular logging mode, it isn't possible to take an online
backup. Therefore a full offline backup functionality will be implemented by
this feature [1]_ . At this time, incremental backups for db2 will not be
supported. The LIST UTILITIES command will be used to monitor the
process. [2]_

Backup
------

The backup procedure for DB2 will follow a process as below. [3]_

* Determine the directory where the backups are written. For DB2 databases
  the default directory location can be found in the config file (/etc/db2/db2
  .conf)
* Check if sufficient disk space is available for the backup on the instance.
* Initiate a DB2 backup through the cli. The BACKUP DATABASE command will be
  used for this purpose.
* Once the backup is complete, compress/encrypt the backup inside the volume
  storage. The name of the backup file will have the following format -
  DB_alias.Type.Inst_name.NODEnnnn.CATNnnnn.timestamp.Seq_num
* The db2ckbkp command will be used to display information about existing
  backup images. This will verify the newly created database backup.
* The compressed/encrypted file can then be stored in Swift under the
  database_backups container.
* The old backup files can then be deleted on the VM once stored in Swift.

Since db2 only supports streaming to named pipes, the backup cannot be
performed in a single step and will first need to store the backup file on
the VM. [4]_

Restore
-------

In order to restore a DB2 database from backup, the following procedure will
be followed. [5]_

* Determine the directory where the backup files are stored
* Ensure that no other applications are running against the database
* Retrieve the backup from storage to the proper location
* Use the RESTORE DATABASE command to recover the database


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

The implmentation of the DB2 backup and restore functionality will allow
users to use several CLI commands for the DB2 datastore.

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

The following commands will be functional for DB2

* backup-create
* backup-delete
* backup-list
* backup-list-instance
* backup-show
* create --backup

Internal API
------------

None

Guest Agent
-----------


The DB2 guest agent will be modified to support backup and restore. In
particular the following files will have added components-

.. code-block:: bash

    guestagent/strategies/backup/experimental/db2_impl.py
    guestagent/strategies/restore/experimental/db2_impl.py

The following existing files will be updated:

.. code-block:: bash

    guestagent/datastore/experimental/db2/manager.py

It will be backwards compatible with API and Task Manager.


Alternatives
------------

The other type of backup that can be implmented is online backup so the
database won't need to shut down before taking backups. However, for online
backups to be implemented, the database must have archive logging options. At
this time it is not possible to specify logging options for DB2 databases in
Trove. Once users can configure other logging options like archive logging,
online backup can be implemented.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  imandhan


Milestones
----------

Target Milestone for completion:

Mitaka-1

Work Items
----------

* Implement backup and restore API calls.
* Write associated test cases.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

Unit tests will be added as necessary for the backup and restore
functionality. Also, a db2 helper will be added to the existing
int-test framework.


Documentation Impact
====================

The DB2 Trove documentation should be updated to indicate that backup and
restore is supported.


References
==========

.. [1] Offline Backup: http://www-01.ibm.com/support/knowledgecenter/SSEPGG_9.7.0/com.ibm.db2.luw.admin.ha.doc/doc/c0051343.html

.. [2] Monitoring Backup: http://www-01.ibm.com/support/knowledgecenter/SSEPGG_9.7.0/com.ibm.db2.luw.admin.ha.doc/doc/t0060260.html

.. [3] DB2 Backup procedure: http://www-01.ibm.com/support/knowledgecenter/SSEPGG_9.7.0/com.ibm.db2.luw.admin.ha.doc/doc/c0006150.html

.. [4] DB2 backing up to named pipe: https://www-01.ibm.com/support/knowledgecenter/SSEPGG_9.5.0/com.ibm.db2.luw.admin.ha.doc/doc/t0006202.html

.. [5] DB2 Restore procedure: http://www-01.ibm.com/support/knowledgecenter/SSEPGG_9.7.0/com.ibm.db2.luw.admin.ha.doc/doc/c0006237.html


Appendix
========

None
