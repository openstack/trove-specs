..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

============================
Vertica Configuration Groups
============================

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/vertica-configuration-groups

Problem Description
===================

The Vertica guestagent currently does not support configuration groups for the
single instance case.

Proposed Change
===============

While Vertica has minimal required configuration as one of its design goals, it
is nonetheless possible to configure a large number of parameters [1]_.

Databases in Trove and Vertica
------------------------------

While Trove thinks of instances as being the parent of one or more databases,
following the model of single-server MySQL, Vertica supports one or more nodes
natively, and databases can span multiple nodes. Configuration options can
also be applied at both the node and database level.

The Vertica guest agent currently does not support multiple Vertica databases
for both the single instance and clustered cases, so only configuration
options valid at the database level will be exposed.

Configuration Changes
---------------------

Vertica recommends against writing configuration changes to a configuration
file for version 7.1. It is unclear if this applies to 7.2, or has been
remedied, but for the purposes of providing support for both 7.1 and 7.2,
writing to this file will be avoided [3]_. Configurations can be applied with
the use of the ALTER DATABASE command, and current configuration settings can
be retrieved via the CONFIGURATION_PARAMETERS system view [2]_.

Vertica supports 360 different options as of Vertica 7.2.1. Options related to
authentication and big data support have been excluded. For a complete list of
the options that will be supported, see the Appendix section.

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

Python API
----------

None (empty section added after merging)

CLI (python-troveclient)
------------------------

None (empty section added after merging)

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

Note that the configuration groups API is not currently supported for clusters,
so only support for single-instance Vertica will be provided.

Guest Agent
-----------

* Implement *update_overrides* and *apply_overrides* in the *manager* and
  *service* modules.

The following existing files will be updated:

    .. code-block:: bash

        guestagent/datastore/experimental/vertica/manager.py
        guestagent/datastore/experimental/vertica/service.py
        guestagent/datastore/experimental/vertica/system.py

Alternatives
------------

None

Implementation
==============

Assignee(s)
-----------

Alex Tomic <atomic@tesora.com>

Milestones
----------

mitaka-3

Work Items
----------

- provide support for viewing and modifying the vertica database-level
  configuration options

- implement configuration-related manager API calls:

   .. code-block:: python

      def update_overrides(self, context, overrides, remove=False)
      def apply_overrides(self, context, overrides)

Upgrade Implications
====================

None.

Dependencies
============

None.

Testing
=======

Unit tests will be added to validate implemented functions, and integration
tests added or modified from the new scenario testing framework as needed.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

Dashboard Impact (UX)
=====================

None.

Appendix
========

The following is the list of parameters that will be supported:

ActivePartitionCount
AddressCollectorInterval
AdvanceAHMInterval
AHMBackupManagement
AllowNonAsciiNames
AnalyzeRowCountInterval
AnalyzeStatsPlanMaxColumns
AnalyzeStatsSampleBands
ARCCommitPercentage
AuditConfidenceLevel
AuditErrorTolerance
BasicVerticaOptions
BlockCacheSize
BufferQueryOutputForPossibleRetry
CachePositionIndex
CascadeResourcePoolAlwaysReplan
CatalogCheckpointChunkSizeKB
CatalogCheckpointMinLogSizeKB
CatalogCheckpointPercent
CatalogDeindexRename
CheckCRCs
CheckDataTargetSortOrder
ClusterRecoveryWait
CollationExpansion
CompressCatalogOnDisk
CompressDistCalls
CompressNetworkData
ComputeApproxNDVsDuringAnalyzeStats
ContainersPerProjectionLimit
CopyFromVerticaWithIdentity
DatabaseHeartbeatInterval
DBDCorrelationSampleRowCount
DBDCorrelationSampleRowPct
DBDCountDistinctSampleRowCount
DBDCountDistinctSampleRowPct
DBDDeploymentParallelism
DBDDynamicSampling
DBDEncodingSampleRowCount
DBDEncodingSampleRowPct
DBDLargestTableRowCountBoundary
DBDLogInternalDesignProcess
DBDMaxConcurrencyForEncodingExperiment
DBDRepLargeRowCountPct
DBDRepSmallRowCountPct
DBDSampleStorageBandCount
DBDSkewDetectionSampleRowCount
DBDSkewDetectionSampleRowPct
DBDUseOnlyDesignerResourcePool
DefaultIntervalStyle
DefaultSessionLocale
DisableInheritedPrivileges
DisableLocalResegmentation
DisableNodeDownOptimization
DisablePrejoinProjections
DisallowMars
DiskSpacePollingInterval
DMLCancelTM
EEVerticaOptions
EnableAccessPolicy
EnableAllRolesOnLogin
EnableApportionLoad
EnableAutoDMLStats
EnableBlockMemoryManager
EnableCooperativeParse
EnableDataCollector
EnabledCipherSuites
EnableEEThreadPool
EnableEMMJMultiblockSIPS
EnableExprsInProjections
EnableForceOuter
EnableGroupByProjections
EnableJIT
EnableNewPrimaryKeysByDefault
EnableNewUniqueKeysByDefault
EnableParallelHashBuild
EnableParallelSort
EnablePatternMatchingAnyRow
EnablePlanStability
EnablePlanStabilityLookup
EnableResourcePoolCPUAffinity
EnableRuntimePriorityScheduler
EnableSSL
EnableStorageBundling
EnableStrictTimeCasts
EnableTopKProjections
EnableUDTProjections
EnableUniquenessOptimization
EnableVirtualCoreCount
EpochMapInterval
EscapeStringWarning
EvaluateDeletePerformanceSampleStorageBandCount
EvaluateDeletePerformanceSampleStorageCount
ExcludeEphemeralNodesInQueries
ExternalTablesExceptionsLimit
FailoverToStandbyAfter
FencedUDxMemoryLimitMB
FilesPerProjectionLimit
FlexTableDataTypeGuessMultiplier
FlexTableRawSize
ForceUDxFencedMode
FsyncCatalogForLuck
FsyncDataForLuck
GBHashMemCapMB
GlobalEEProfiling
GlobalHeirUsername
GlobalQueryProfiling
GlobalSessionProfiling
GroupGeneratorHashingEnabled
HadoopConfDir
HCatConnectionTimeout
HCatParserName
HCatSlowTransferLimit
HCatSlowTransferTime
HCatSourceName
HCatWebserviceName
HCatWebserviceVersion
HistoryRetentionEpochs
HistoryRetentionTime
JavaBinaryForUDx
JavaSideProcessMinHeapSizeMB
KeepMinMaxOnAllColumns
LGELagThreshold
LoadMaxFinalROSCount
LockTimeout
LogHeartbeatInterval
LowDiskSpaceWarningPct
MaxAutoSegColumns
MaxBundleableROSSizeKB
MaxClientSessions
MaxConstraintChecksPerQuery
MaxDataCollectorFileSize
MaxDesiredEEBlockSize
MaxDVROSPerContainer
MaxLogLineLength
MaxMrgOutROSSizeMB
MaxOptMemMB
MaxOptMemMBInDBD
MaxParsedQuerySizeMB
MaxPartitionCount
MaxQueryRetries
MaxRecoverErrors
MaxRecoverHistoricPasses
MaxRefreshErrors
MaxRefreshHistoricPasses
MaxROSPerStratum
MergeJoinInnerInitialMB
MergeOutCache
MergeOutInterval
MinimumCatalogDiskMegabytes
MinimumDataDiskMegabytes
MinimumDataDiskTempMegabytes
MinSortMergeJoinMB
MoveOutInterval
MoveOutMaxAgeEpochs
MoveOutMaxAgeTime
MoveOutSizePct
NewEEGroupBySmallMemMB
NewEEROSSubdivisionRows
NewEEThreads
NoRecoverShutdownWait
OptVerticaOptions
ParallelizeLocalSegmentLoad
PatternMatchAllocator
PatternMatchingMatchLimitRecursion
PatternMatchingMaxPartition
PatternMatchingMaxPartitionMatches
PatternMatchingPerMatchWorkspaceSize
PatternMatchingUseJit
PatternMatchStackAllocator
PinProcessors
PinProcessorsOffset
PreExcavatorReplicatedProjection
PruneDataCollectorByTime
PruneSystemTableColumns
PurgeMergeoutPercent
RangeWindowMaxMem
ReapBeforeRecover
RecoverByContainer
RecoveryDirtyTxnWait
ReflexiveMoveout
RefreshByContainer
RemoteInitiatorBufSize
RemoveSnapshotInterval
ReplayDeleteAlgorithmSwitchThreshold
ResLowLimPctOfHighLim
RestrictSystemTables
ROSCacheBlocks
ROSCacheLargeBlocks
ROSPerStratum
SaveDCEEProfileThresholdUS
SecurityAlgorithm
SegmentAutoProjection
SegmentDataCollector
SessionProfilingAgeOut
SlowDeleteConsoleWarningLimit
SlowDeleteSystemWarningLimit
SmallROSSize
SnapshotRetentionTime
SnmpTrapDestinationsList
SnmpTrapEvents
SnmpTrapsEnabled
SortCheckOption
SortOrderReportLevel
SortWorkerThreads
SSLCA
SSLCertificate
SSLPrivateKey
StandardConformingStrings
StrictUDxParameterChecking
SyslogEnabled
SyslogEvents
SyslogFacility
SystemMonitorInterval
SystemMonitorThreshold
TerraceRoutingFactor
TextIndexComputeDeletedTokens
TextIndexMaxTokenLength
TopKHeapMaxMem
TransactionIsolationLevel
TransactionMode
TrustConstraintsAsUnique
UDxFencedBlockTimeout
UDxFencedCancelTimeout
UDxFencedExternalProcedureTimeout
UseModularHashForReseg
UseOnlyResilientRedistribution
UseRecoveringNodesInVirtualTableQueries
UseSafeDecompression
UseV50IntegerDivision
UseZygoteForExternalProcedures
WarnOnIncompleteStartupPacket
WithClauseMaterialization

References
==========

.. [1] https://my.vertica.com/docs/7.2.x/HTML/index.htm#Authoring/AdministratorsGuide/ConfiguringTheDB/ConfiguringTheDatabase.htm
.. [2] https://my.vertica.com/docs/7.2.x/HTML/Content/Authoring/SQLReferenceManual/SystemTables/MONITOR/CONFIGURATION_PARAMETERS.htm
.. [3] https://my.vertica.com/docs/7.2.x/HTML/index.htm#Authoring/AdministratorsGuide/ConfiguringTheDB/SettingandClearingConfigParameters.htm
