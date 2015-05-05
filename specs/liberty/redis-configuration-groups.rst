..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

==========================
Redis Configuration Groups
==========================

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/redis-configuration-groups

Problem description
===================

The Redis guestagent currently does not support configuration groups.

Proposed change
===============

The patch set will implement configuration groups for Redis 3.0 or above.

Redis stores its configuration [1]_ in 'redis.conf' file which can optionally
import other files. If there are multiple configuration directives for a single
property the last one is used.
Configuration directives have key-value format:
"keyword argument1 argument2 ... argumentN"

Redis configuration will be reconfigured on the fly without stopping and
restarting the service using the special CONFIG command [1]_.

Note: Not all directives are supported by the CONFIG commands and
that modifying the configuration on the fly has no effects on the 'redis.conf'
file.

The base configuration file for Redis 3.0 [2]_ will be used as the default
configuration template.
Guest agent interfaces exposing the configuration properties will be made
available to other modules such as backup and replication.

Most configuration properties will be available via configuration groups.
Some, however, do not make sense in the Trove context.

These include:

   - irrelevant options (like automatic snapshots, since the Trove user cannot
     retrieve them)
   - guestagent specific (e.g. file paths, passwords)
   - items that Trove needs to control (replication/clustering properties)

See `Available Configuration Properties`_ for the full list of supported
options.

The CONFIG directives will be renamed to a name known only to the
guestagent for its internal use. This is to prevent a user from
bypassing Trove configuration groups by changing properties in the client.
Guestagent managed properties such as locations of database files and logs
could be potentially used to hijack the NOVA instance.

Configuration overrides will be implemented using the in-file imports
supported by the Redis configuration file format.
User defined overrides if any, will be saved in 'redis.conf.override'
and will be imported at the end of the default 'redis.conf' file.

Available Configuration Properties
----------------------------------

Keys not included in the lists are kept at their default values and are not
configurable via Trove. See [2]_ for more details and default values.

The properties configurable by the user via the Trove API:

   - tcp-backlog
   - timeout
   - tcp-keepalive
   - loglevel
   - databases
   - save
   - stop-writes-on-bgsave-error
   - rdbcompression
   - rdbchecksum
   - slave-serve-stale-data
   - slave-read-only
   - repl-diskless-sync
   - repl-diskless-sync-delay
   - repl-ping-slave-period
   - repl-timeout
   - repl-disable-tcp-nodelay
   - repl-backlog-size
   - repl-backlog-ttl
   - slave-priority
   - min-slaves-to-write
   - min-slaves-max-lag
   - requirepass
   - maxclients
   - maxmemory
   - maxmemory-policy
   - maxmemory-samples
   - appendonly
   - appendfsync
   - no-appendfsync-on-rewrite
   - auto-aof-rewrite-percentage
   - auto-aof-rewrite-min-size
   - aof-load-truncated
   - lua-time-limit
   - cluster-node-timeout
   - cluster-slave-validity-factor
   - cluster-migration-barrier
   - cluster-require-full-coverage
   - slowlog-log-slower-than
   - slowlog-max-len
   - latency-monitor-threshold
   - notify-keyspace-events
   - hash-max-ziplist-entries
   - hash-max-ziplist-value
   - list-max-ziplist-entries
   - list-max-ziplist-value
   - set-max-intset-entries
   - zset-max-ziplist-entries
   - zset-max-ziplist-value
   - hll-sparse-max-bytes
   - activerehashing
   - client-output-buffer-limit normal
   - client-output-buffer-limit slave
   - client-output-buffer-limit pubsub
   - hz
   - aof-rewrite-incremental-fsync

Non-configurable properties with updated default values:

   - *daemonize* **yes**
   - *pidfile* **(controlled-by guestagent)**
   - *logfile* **(controlled-by guestagent)**
   - *dir* **(controlled-by guestagent)**
   - *slaveof* **(controlled-by replication)**
   - *masterauth* **(controlled-by guestagent)**
   - *cluster-enabled* **(controlled-by clustering)**
   - *cluster-config-file* **(controlled-by guestagent)**

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

* Update facilities for handling of Redis config files
  in the *operating_system* module.
* Implement *update_overrides* and *apply_overrides* in
  the *manager* and *service* modules.
* The current configuration template will be updated to [2]_
  with changes noted in `Available Configuration Properties`_.

The following existing files will be updated:

    .. code-block:: bash

        guestagent/datastore/experimental/redis/manager.py
        guestagent/datastore/experimental/redis/service.py
        templates/redis/config.template

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

1. Implement functionality to handle (read/write/update) Redis configuration
   files.
2. Implement configuration-related manager API calls:

   .. code-block:: python

      def update_overrides(self, context, overrides, remove=False)
      def apply_overrides(self, context, overrides)

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

.. [1] Documentation on Redis configuration: http://redis.io/topics/config
.. [2] Self-documented configuration file for Redis 3.0: https://raw.githubusercontent.com/antirez/redis/3.0/redis.conf
