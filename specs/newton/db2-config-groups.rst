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


=======================================
Configuration Group Management for DB2
=======================================

This spec talks about how to enable configuration group management
for DB2.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/db2-config-group


Problem Description
===================

Trove supports configuration group management but this feature has not been
implemented for DB2.


Proposed Change
===============

DB2 supports both database manager configuration parameters and database
configuration parameters. The database manager configuration parameters
apply to an instance whereas the database configuration parameter applies
to each database. In this spec, we talk about implementing configuration
management for the DB2 database manager.

The database manager configuration parameters are stored in the db2systm file
under the sqllib directory. To update the configuration parameters, DB2
recommends using the UPDATE DBM CONFIGURATION and RESET DBM CONFIGURATION
commands instead of directly updating the config file. To see a complete list
of configuration parameters, check the Appendix section.

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

None

CLI (python-troveclient)
------------------------

None

Internal API
------------

None

Guest Agent
-----------

Implement update_overrides and apply_overrides in the manager and service
modules.

    The following files will be updated::

    /opt/stack/trove/trove/guestagent/datastore/experimental/db2/manager.py
    /opt/stack/trove/trove/guestagent/datastore/experimental/db2/service.py
    /opt/stack/trove/trove/guestagent/datastore/experimental/db2/system.py

    The following file will be added::

    /opt/stack/trove/trove/templates/db2/validation-rules.json

This will fit into the existing configuration manager framework. The existing
'PropertiesCodec' implementation will be reused to handle text-file operations.
Configuration overrides will be implemented using the 'ImportStrategy' of the
guestagent configuration manager.

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

mariamj@us.ibm.com

Milestones
----------

Newton

Work Items
----------

Implement configuration-related manager API calls

    .. code-block:: python

        def update_overrides(self, context, overrides, remove=False)
        def apply_overrides(self, context, overrides)

Write unit tests/integration tests were applicable


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

- Unit and integration tests will be added to test the new functionality


Documentation Impact
====================

The documentation will be updated to reflect the new features supported by
Trove for DB2.


References
==========

.. [1] https://www.ibm.com/support/knowledgecenter/SSEPGG_10.5.0/com.ibm.db2.luw.admin.config.doc/doc/c0060794.html

Appendix
========

The database manager configuration parameters have been listed below. For a
detailed description of each parameter, please refer[1]. The parameters listed
below are the ones that are relevant for the DB2 Express-C version. The link
referenced in [1] gives a complete list of parameters for the DB2 enterprise
edition::

    AGENTPRI
    AGENT_STACK_SZ
    ALTERNATE_AUTH_ENC
    ASLHEAPSZ
    AUDIT_BUF_SZ
    CATALOG_NOAUTH
    CLNT_KRB_PLUGIN
    CLNT_PW_PLUGIN
    COMM_EXIT_LIST
    CUR_EFF_ARCH_LVL
    CUR_EFF_CODE_LVL
    DFT_ACCOUNT_STR
    DFT_MON_BUFPOOL
    DFT_MON_LOCK
    DFT_MON_SORT
    DFT_MON_STMT
    DFT_MON_TABLE
    DFT_MON_TIMESTAMP
    DFT_MON_UOW
    DIAGLEVEL
    DIAGSIZE
    DIR_CACHE
    DISCOVER
    DISCOVER_INST
    FCM_NUM_BUFFERS
    FCM_NUM_CHANNELS
    FEDERATED
    FED_NOAUTH
    FENCED_POOL
    GROUP_PLUGIN
    HEALTH_MON
    INDEXREC
    INTRA_PARALLEL
    JAVA_HEAP_SZ
    KEEPFENCED
    KEYSTORE_TYPE
    LOCAL_GSSPLUGIN
    MAX_CONNECTIONS
    MAX_COORDAGENTS
    MAX_QUERYDEGREE
    MON_HEAP_SZ
    NOTIFYLEVEL
    NUMDB
    NUM_INITAGENTS
    NUM_INITFENCED
    NUM_POOLAGENTS
    RESYNC_INTERVAL
    RQRIOBLK
    SHEAPTHRES
    SPM_LOG_FILE_SZ
    SPM_MAX_RESYNC
    SRVCON_AUTH
    SRVCON_GSSPLUGIN_LIST
    SRVCON_PW_PLUGIN
    SRV_PLUGIN_MODE
    SSL_CIPHERSPECS
    SSL_CLNT_KEYDB
    SSL_CLNT_STASH
    SSL_SVCENAME
    SSL_SVR_KEYDB
    SSL_SVR_LABEL
    SSL_SVR_STASH
    SSL_VERSIONS
    START_STOP_TIME
    SYSADM_GROUP
    SYSCTRL_GROUP
    SYSMAINT_GROUP
    SYSMON_GROUP
    TM_DATABASE
    TP_MON_NAME
    TRUST_ALLCLNTS
    TRUST_CLNTAUTH
    UTIL_IMPACT_LIM
    WLM_DISPATCHER
    WLM_DISP_CONCUR
    WLM_DISP_CPU_SHARES
    WLM_DISP_MIN_UTIL

Guest agent controlled parameters::

    ALT_DIAGPATH
    AUTHENTICATION
    DFTDBPATH
    DIAGPATH
    JDK_PATH
    KEYSTORE_LOCATION
