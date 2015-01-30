..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

=======================
Trove Replication V2
=======================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/trove/bp/replication-v2

The Juno release of Trove laid the foundation of Trove Replication
support.  The V1 version of replication focused on providing read-only
slave replication in MySQL 5.5.  For the V2 replication release for
Kilo, replication will be extended to provide support for manual
failover in MySQL replication leveraging the latest replication
features of MySQL 5.6.

Problem description
===================

For the Kilo release of OpenStack, trove replication support will be
extended to support manual failover when a replication master fails.
Specifically, this means that a user can instruct Trove to demote a
replication master and promote a slave to be the new master.  For V2,
manual promotion means that the user will be required to execute an
action to cause failover - a component to detect failure and cause the
failover to occur will not be within the scope of V2.


Proposed change
===============

Supported Features:

* manual failover
* master/slaves in different availability zones
* automatic slave generation to replace slaves promoted to master
* automatically generated slave will be created in the same az as the
  slave that was promoted to master
* public ips assigned to deleted/demoted master will be transferred to
  new master
* public ips of promoted slave will be transferred to new slave
* GTIDs will be used to facilitate master promotion (Note: this limits
  feature set to MySQL 5.6 and later)
* if a master site is reachable, a chosen slave may be promoted to
  master and the old master will be demoted to a slave.  This
  operation will be done in such a way as to prevent the loss of data.
  This operation would be useful for resizing a master without
  downtime.
* a master site may be deleted, in which case Trove will pick a slave
  to be promoted to master (see MASTER_PROMOTION_STRATEGY below) and a
  new slave will be generated to replace the promoted slave.  If the
  master site in not reachable, it will be forcefully removed from
  Trove/Nova; this is how an unreachable master would be "failed
  over".
* new master selection process on delete has following
  MASTER_PROMOTION_STRATEGY (CONF) switch: MOST_RECENT: the slave with
  the most recent updates is chosen as new master, PROXIMATE_AZ: slave
  IN MASTER's AZ with most recent updates is chosen as new master,
  PROXIMATE_REGION: slave IN MASTER's REGION with most recent update
  is chosen as new master.  PROXIMATE_REGION will be the default
  (though for now equivalent to MOST_RECENT) and may be the only
  implemented option for V2.
* replication from existing backup and incremental snapshot will be
  implemented
* replica_count option will be added to create-instance to allow N
  slaves to be spun up from a given snapshot.  All replicas from the
  given snapshot will have the same "create-instance" options.

Features Not Supported:

* automatic failover
* region support
* writable slaves
* features related to the promotion of slaves to masters will not be
  supported by MySQL versions prior to 5.6
* replication_strategy per datastore - this could be implemented in
  Kilo via an independent blueprint
* GTID based replication for MariaDB (binlog replication will not be
  tested for MariaDB, but should be compatible with MySQL)
* host affinity/anti-affinity
* dealing with "error transactions" created when updates are executed
  directly on slaves in conflict with changes on the master.
  Performing updates directly on slaves is not supported by Trove and
  slave sites will be put into "read only" mode.

Replication V2 Components
-------------------------

The V2 Replication feature will consist of several components:

- Implement a new replication strategy to support GTID Based
  Replication in addition to Bin Log replication.
- Manual failover from replication master
- Replication configuration using incremental snapshots based on
  existing backups.
- Creation of multiple slaves from master in single call

Upgrade from Binlog Replication to GTID Based Replication
*********************************************************

MySQL 5.6 introduced a new type of replication which is based on
Global Transaction IDs (GTID).  By assigning a GTID to each
transaction, MySQL is able to simplify transaction coordination
between masters and slaves, allowing for simpler and more reliable
failover to a new master.

This feature requires that the trove-integration project upgrade to
use Ubuntu 14.04 and MySQL 5.6.

A new Replication Strategy named "MysqlGTIDReplicationStrategy" will
be created to support the new GTID based replication with MySQL 5.6
and later, and the existing Replication Strategy named
"MysqlBinlogReplication" will continue to be supported for MySQL 5.5
but without support for the new features listed in this document.


Manual Failover from Replication Master
***************************************

It will be possible for a user to cause a slave to become the new
master for replication by executing a trove command.  For the V2
release of replication, no facility for detecting a master failure
condition will be provided.

To assist the user in minimizing data loss, there will be two
different ways for the user to cause a slave to be promoted to master.
If the user wishes to promote a slave to replace a master which is
healthy and reachable, they will execute a new
"promote_to_replica_source" function against a slave to promote it in
place of the existing master; this function will coordinate with the
master site to ensure that no data is lost.  If a master site is
unreachable, the user will use the "eject_replica_source" function to
remove that instance from the replication set and the replication
strategy will choose the slave with the most recent updates to promote
to master; this operation may result in the loss of any transactions
that were committed at the master site but not replicated to any of
the slaves.  Trove will not allow a reachable master site to be
deleted as that would unnecessarily result in lost data.

There will be no accomodation made to allow users or operators to
"fix" slaves which have gotten out of sync with the master site.
Instead, every effort will be made to configure replication so that
the slave will not fall out of sync with the master.  The following
MySQL options will be set to ensure safe replication:

*Master Options*

* Binary logs will be configured for MIXED mode logging.  This will
  allow statement based replication where it is safe to do so, and row
  based replication will be used where necessary.
* The enforce_gtid_consistency option will be used to prevent
  statements which will conflict with the use of GTID replication.
* When the Percona database is being used, the Percona
  enforce_storage_engine option will be used to restrict replication
  to the InnoDB storage engine.  This is to prevent the use of MyISAM
  tables which could be corrupted during a crash recovery.

*Slave Options*

* Slave will execute in READ_ONLY mode to avoid transaction conflicts
  between master and slave.  By default, users are not given root
  access to the database; if they choose to enable root access, they
  are assumed to be sufficiently advanced as to not execute operations
  on a slave which will disturb replication.
* The slaves' relay log will be stored in a table in the database to
  provide transactional consistency between the statements executed
  against the database and the recording of the slave's position in
  executing the relay log.
* Relay log recovery will be turned on to cause relay log recovery
  during mysql startup.  relay_log_purge will be enabled in support
  for relay_log_recovery.

Promotion of Slave to Master
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The user may select a slave to be promoted to be the new master of a
replication set.  This operation would consist of the following steps:

#. Contact each slave, abort operation if any not reachable
#. Make the old master read-only
#. Detach old master's public IP
#. Detach master candidate's public IP
#. Record latest GTID of master
#. For each slave (including master candidate)

   * Wait for slave to receive/apply master's latest GTID
#. Set master candidate as replication master site
#. For each remaining slave

   * Make instance slave of new master
#. Make old master be slave of new master
#. Assign master candidate's IP to old master (which is now slave)
#. Make new master writable
#. Assign old master's public IP to new master

*Promote to Master API*

To replace a healthy master site, the promote_to_replica_source API
call will be added to the client and taskmanager APIs.

Ejection of Master Site
^^^^^^^^^^^^^^^^^^^^^^^

If a replication master site is out of service, the user may choose to
"eject" the instance from the replication set.  Ejecting an
unreachable instance which is a master for replication would result in
one of its slaves being chosen to be promoted to be the new master
site, and a new slave generated to fill out the replication set.  The
ejected master will be available for examination, but will no longer
participate in replication.  This operation would consist of the
following steps:

#. Abort operation if the master site can be contacted
#. Contact each slave, abort operation if any not reachable
#. Detach master's public IP
#. Record master's Region/Zone
#. Select master candidate (see Master Candidate Selection)
#. Switch the master candidate from slave to master
#. For each remaining slave

   * Connect slave to new master instance
#. Mark new master as writable
#. Attach master's public IP to new master
#. Create new slave in same Region/Zone as old master
#. Assign master candidate's public IP to new slave

*Master Candidate Selection*

When selecting a slave to be promoted to master to replace an
unreachable master site, the algorithm for choosing the master
candidate will be determined by the value of the
MASTER_PROMOTION_STRATEGY configuration option of the Taskmanager
Config (not datastore specific).  The possible values for this option
are outlined below:

================ =================================================
Strategy         Description
================ =================================================
MOST_RECENT      The slave with the highest GTID is chosen as the
                 master candidate
PROXIMATE_AZ     The slave with the highest GTID in the same
                 Availability Zone as the old master is chosen
PROXIMATE_REGION The slave with the highest GTID in the same
                 Region as the old master is chosen
================ =================================================

The PROXIMATE_REGION setting will be the default as this will ensure
that the new master site will be in the same region as the old master;
for the Kilo release, this will be equivalent to the MOST_RECENT
option (and may be implemented as such) as Region support is not
implemented in Trove.


Incremental Snapshots
*********************

To improve the performance of slave creation, the default action will
be to take the most recent backup (full or incremental) and create an
incremental backup to be used for the replication snapshot.  If no
previous backup can be found, a full backup will be created to include
in the replication snapshot.  Should the "backup" option be specified
in addition to the "replica_of" option, an incremental backup will be
performed from the indicated backup.


Multiple Slave Creation
***********************

A replica_count option will be added to support the creation of multiple
slaves from a single replication snapshot.

* a replica_count option will be added to the ``trove create`` command
* a replica_count parameter will be added to the create_instance
  taskmanager ReST API
* the taskmanager FreshInstanceTasks.create_instance method will
  iteratively create the specified number of slaves from a single
  replication snapshot (the implementor is free to implement slave
  creation in parallel if time permits, and should investigate doing
  so, but it is not a requirement for V2)

Configuration
-------------

MysqlGTIDReplicationStrategy value added to ReplicationStategy option
for MySQL configuration.

New configuration option master_promotion_strategy added to MySQL
configuration with values as above.

Database
--------

No database impacts are envisioned.


Public API
----------

*Promote to Replica Source*

A new action will be added to the Trove REST API to allow a replica to
be promoted to be the master of its replication set::

  POST http://127.0.0.1:8779/v1.0/<tenant id>/instance/<instance id>/action
  {
      *"promote_to_replica_source": null*
  }

  RESP: [200]
    {
        'date': '<date>',
        'content-length': '<RESP BODY len>',
        'content-type': 'application/json'
    }
  RESP BODY:
    {
        "instance": {
            *"status": "PROMOTE",*
            "updated": "2014-11-25T21:25:11",
            "name": "m",
            "links": [
                {
                    "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/instances\/...",
                    "rel": "self"
                },
                {
                    "href": "https:\/\/10.40.10.178:8779\/instances\/...",
                    "rel": "bookmark"
                }
            ],
            "created": "2014-11-25T21:25:06",
            "ip": [
                "10.0.0.2"
            ],
            "replicas": [
                {
                    "id": "8e5710df-ef39-4201-a059-764d9091f079",
                    "links": [
                        {
                            "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/instances\/...",
                            "rel": "self"
                        },
                        {
                            "href": "https:\/\/10.40.10.178:8779\/instances\/...",
                            "rel": "bookmark"
                        }
                    ]
                }
            ],
            "id": "fff6d8c5-9d05-4a00-ab58-d8954ec945a3",
            "volume": {
                "used": 0.13,
                "size": 1
            },
            "flavor": {
                "id": "7",
                "links": [
                    {
                        "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/flavors\/7",
                        "rel": "self"
                    },
                    {
                        "href": "https:\/\/10.40.10.178:8779\/flavors\/7",
                        "rel": "bookmark"
                    }
                ]
            },
            "datastore": {
                "version": "5.5",
                "type": "mysql"
            }
        }
    }

A new CLI command will be added to invoke the
promote_to_replica_source API::

  trove promote-to-replica-source <replica id>

*Eject Replica Source*

A new action will be added to the Trove REST API to allow a replica
source to be ejected from a replication set::

  POST http://127.0.0.1:8779/v1.0/<tenant id>/instance/<instance id>/action
  {
      *"eject_replica_source": null*
  }

  RESP: [200]
    {
        'date': '<date>',
        'content-length': '<RESP BODY len>',
        'content-type': 'application/json'
    }
  RESP BODY:
    {
        "instance": {
            *"status": "EJECT",*
            "updated": "2014-11-25T21:25:11",
            "name": "m",
            "links": [
                {
                    "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/instances\/...",
                    "rel": "self"
                },
                {
                    "href": "https:\/\/10.40.10.178:8779\/instances\/...",
                    "rel": "bookmark"
                }
            ],
            "created": "2014-11-25T21:25:06",
            "ip": [
                "10.0.0.2"
            ],
            "replicas": [
                {
                    "id": "8e5710df-ef39-4201-a059-764d9091f079",
                    "links": [
                        {
                            "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/instances\/...",
                            "rel": "self"
                        },
                        {
                            "href": "https:\/\/10.40.10.178:8779\/instances\/...",
                            "rel": "bookmark"
                        }
                    ]
                }
            ],
            "id": "fff6d8c5-9d05-4a00-ab58-d8954ec945a3",
            "volume": {
                "used": 0.13,
                "size": 1
            },
            "flavor": {
                "id": "7",
                "links": [
                    {
                        "href": "https:\/\/10.40.10.178:8779\/v1.0\/...\/flavors\/7",
                        "rel": "self"
                    },
                    {
                        "href": "https:\/\/10.40.10.178:8779\/flavors\/7",
                        "rel": "bookmark"
                    }
                ]
            },
            "datastore": {
                "version": "5.5",
                "type": "mysql"
            }
        }
    }

A new CLI command will be added to invoke the eject_replica_source
API::

  trove eject-replica-source <replica source id>


*Trove Create Replica Count*

The Trove REST API for the create instance operation will be augmented
with a new field *replica_count* to specify the number of replicas to
be created from the indicated instance::

  POST http://127.0.0.1:8779/v1.0/<tenant id>/instances
  {
      "instance": {
          "volume": {"size": 1},
          "flavorRef": "7",
          "name": "s",
          "replica_of": "<master id>",
          *"replica_count": "<n>"*
      }
  }

  RESP *unchanged*

An option will be added to the "trove create" CLI command to specify
the new replica count option::

  trove create <name> <flavor id> --replica_count=<count> ...


Internal API
------------

promote_to_replica_source method added to taskmanager API.
eject_replica_source method added to taskmanager API.

Guest Agent
-----------

The implementation of this feature set will result in many additions
to the MySQL guest agent.  There should be minimal impact to
pre-existing code, and there is not expected to be any impact on
backward compatibility of the APIs.

Alternatives
------------

None.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vgnbkr

Secondary assignee:
  peterstac

Milestones
----------

Target Milestone for completion:
  Kilo-2

Work Items
----------

====================== ========= =================
Work Item              Assignee  Scheduled Release
====================== ========= =================
GTID Support           Morgan    Kilo-3
Failover               Morgan    Kilo-3
Slave Count            Peter     Kilo-3
Incremental Snapshots  Peter     Kilo-3
====================== ========= =================


Dependencies
============

n/a

Testing
=======

The existing int-tests are believed to be sufficient for testing the
GTID replication changes, as there are no functionality changes, just
implementation changes.

New Int-Tests:

Promote to Master Positive

    Create a new replication set of two sites.  Attach floating ip
    addresses to each instance.  Execute the promote_to_replica_source
    API call and verify that the master/slave relationships are
    correctly changed, and that the floating ip addresses maintain
    their affinity to master and slave.

Promote to Master Negative

    Create a new replication set of two sites. Execute "service mysql
    stop" on the master site.  Verify that promote_to_replica_source
    cannot be executed against the slave site.

Delete Master Positive

    Create a new replication set of two sites.  Attach floating ip
    addresses to each instance.  Execute "service mysql stop" on the
    master to simulate the master site crashing.  Execute the delete
    API call against the master site.  Ensure that the slave has been
    promoted to master, a new slave has been added, and that the
    floating ip addresses have been moved appropriately.

Replica Count

    No int-test will be done for this feature due to the resource
    requirements

Incremental Snapshots

    No int-test will be done for this feature as there is no way to
    verify that the restore was actually done from an incremental
    backup rather than a full backup


Documentation Impact
====================

User Guide
----------

* add section explaining manual failover, both via
  promote-to-replica-source and via deletion of a failed master
* section on replication should be updated to document replica_count
  option to "trove create"

CLI Reference
-------------

* add promote-to-replica-source command
* add eject-replica-source command
* update create command with replica_count


References
==========

- https://etherpad.openstack.org/p/kilo-summit-trove-replication-v2

