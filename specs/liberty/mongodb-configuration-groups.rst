..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

============================
MongoDB Configuration Groups
============================

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/mongodb-configuration-groups

Problem description
===================

The MongoDB guestagent currently does not support configuration groups.

Proposed change
===============

The patch set will implement configuration groups for MongoDB 2.6 and above.

MongoDB 2.6 and above stores its configuration [1]_ in a YAML 'mongod.conf'
file.
The database service has to be restarted for any changes to the
configuration file to take effect. All configuration changes will therefore be
requiring database restart and 'apply_overrides' will be implemented as no-op.

Overrides will be implemented by replacing the current file with an
updated one.
The old file will be backed up in the same directory (as *\*.old*) and
restored on configuration reset.

The platform-default configuration file will be used as a base for our
configuration template.
Guest agent interfaces exposing the configuration properties will be made
available to other modules such as backup and replication.


Most configuration properties will be available via configuration groups.
Some, however, do not make sense in the Trove context.

These would include:

   - irrelevant options (like automatic snapshots, since the Trove user cannot
     retrieve them)
   - guestagent specific (e.g. file paths, passwords)
   - items that Trove needs to control (replication/clustering properties)

See `Available Configuration Properties`_ for the full list of supported
options.

The user should be able to specify configurations properties as standard Python
YAML objects - key-value pairs and dicts.

Available Configuration Properties
----------------------------------

Keys not included in the lists are kept at their default values and are not
configurable via Trove. See [1]_ for more details and default values.

The properties configurable by the user via the Trove API:

   - systemLog.verbosity
   - systemLog.component.accessControl.verbosity
   - systemLog.component.command.verbosity
   - systemLog.component.control.verbosity
   - systemLog.component.geo.verbosity
   - systemLog.component.index.verbosity
   - systemLog.component.network.verbosity
   - systemLog.component.query.verbosity
   - systemLog.component.replication.verbosity
   - systemLog.component.sharding.verbosity
   - systemLog.component.storage.verbosity
   - systemLog.component.storage.journal.verbosity
   - systemLog.component.write.verbosity
   - systemLog.quiet
   - systemLog.traceAllExceptions
   - systemLog.logAppend
   - systemLog.logRotate
   - systemLog.timeStampFormat
   - net.maxIncomingConnections
   - net.wireObjectCheck
   - net.unixDomainSocket.enabled
   - net.ipv6
   - net.http.enabled
   - net.http.JSONPEnabled
   - net.http.RESTInterfaceEnabled
   - security.sasl.hostName
   - security.sasl.serviceName
   - security.sasl.saslauthdSocketPath
   - security.javascriptEnabled
   - operationProfiling.slowOpThresholdMs
   - operationProfiling.mode
   - storage.indexBuildRetry
   - storage.journal.enabled
   - storage.directoryPerDB
   - storage.syncPeriodSecs
   - storage.engine
   - storage.mmapv1.nsSize
   - storage.mmapv1.quota.enforced
   - storage.mmapv1.quota.maxFilesPerDB
   - storage.mmapv1.smallFiles
   - storage.mmapv1.journal.debugFlags
   - storage.mmapv1.journal.commitIntervalMs
   - storage.wiredTiger.engineConfig.cacheSizeGB
   - storage.wiredTiger.engineConfig.statisticsLogDelaySecs
   - storage.wiredTiger.engineConfig.journalCompressor
   - storage.wiredTiger.engineConfig.directoryForIndexes
   - storage.wiredTiger.collectionConfig.blockCompressor
   - storage.wiredTiger.indexConfig.prefixCompression
   - replication.oplogSizeMB
   - replication.secondaryIndexPrefetch
   - sharding.clusterRole
   - auditLog.format
   - auditLog.filter
   - snmp.subagent
   - snmp.master
   - replication.localPingThresholdMs
   - sharding.autoSplit
   - sharding.configDB
   - sharding.chunkSize
   - setParameter

Non-configurable properties with updated default values:

   - *systemLog.path* **(controlled-by guestagent)**
   - *systemLog.destination* **file**
   - *processManagement.pidFilePath* **(controlled-by guestagent)**
   - *processManagement.fork* **True**
   - *security.keyFile* **(controlled-by replication)**
   - *security.clusterAuthMode* **(keyFile)**
   - *security.authorization* **True**
   - *storage.dbPath* **(controlled-by guestagent)**
   - *replication.replSetName* **(controlled-by replication)**
   - *sharding.archiveMovedChunks* **False**
   - *auditLog.destination* **file**
   - *auditLog.path* **(controlled-by guestagent)**

Configuration
-------------

None

Database
--------

None

Public API
----------

None

Public API Security
-------------------

None

Internal API
------------

CLI (python-troveclient)
------------------------

This work will enable the following client commands:

  * configuration-attach
  * configuration-create
  * configuration-default
  * configuration-delete
  * configuration-detach
  * configuration-instances
  * configuration-list
  * configuration-parameter-list
  * configuration-parameter-show
  * configuration-patch
  * configuration-show
  * configuration-update

Guest Agent
-----------

* Update facilities for handling of YAML config files
  in the *operating_system* module.
* Implement API to *update_overrides* in
  the *manager* and *service* modules.
* The current configuration template will be updated to the default version
  for the target platform with changes noted in
  `Available Configuration Properties`_.

The following existing files will be updated:

    .. code-block:: bash

       guestagent/datastore/experimental/mongodb/manager.py
       guestagent/datastore/experimental/mongodb/service.py
       templates/mongodb/config.template

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

Liberty

Work Items
----------

1. Implement functionality to handle (read/write/update) MongoDB YAML
   configuration files.
2. Implement configuration-related manager API calls.

   .. code-block:: python

      def update_overrides(self, context, overrides, remove=False)
      def apply_overrides(self, context, overrides) [no-op]


Upgrade Implications
====================

None

Dependencies
============

None

Testing
=======

Unit tests will be added to validate implemented functions and non-trivial
codepaths. Relevant integration tests will be added.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] Documentation on MongoDB configuration: http://docs.mongodb.org/manual/reference/configuration-options/
