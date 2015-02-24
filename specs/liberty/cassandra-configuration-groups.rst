..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

==============================
Cassandra Configuration Groups
==============================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/cassandra-configuration-groups

Problem Description
===================

The Cassandra datastore currently does not support configuration groups.

Proposed Change
===============

The patch set will implement configuration groups for Cassandra 2.1.

Configuration
-------------

The configuration template will be updated to the default template for the
target platform.

   *  templates/cassandra/config.template

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

None

Guest Agent
-----------

Cassandra stores its configuration in 'cassandra.yaml' file
(commonly in '/etc/cassandra').
The node (datastore service) has to be restarted for any changes to the
configuration file to take effect. All configuration changes will therefore be
requiring database restart and 'apply_overrides' will be implemented as no-op.

Overrides will be implemented by replacing the current file with an
updated one.
The old file will be backed up in the same directory (as *\*.old*) and
restored on configuration reset.

Most configuration properties will be available via configuration groups.
Some, however, do not make sense in the Trove context.

These include:

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

Properties not included in the lists are kept at their default values
and are not configurable via Trove.

The properties configurable by the user via the Trove API:

   - cluster_name
   - listen_address
   - commit_failure_policy
   - disk_failure_policy
   - endpoint_snitch
   - seed_provider
   - compaction_throughput_mb_per_sec
   - memtable_total_space_in_mb
   - concurrent_reads
   - concurrent_writes
   - phi_convict_threshold
   - commitlog_sync
   - commitlog_segment_size_in_mb
   - commitlog_total_space_in_mb
   - compaction_preheat_key_cache
   - concurrent_compactors
   - in_memory_compaction_limit_in_mb
   - preheat_kernel_page_cache
   - sstable_preemptive_open_interval_in_mb
   - memtable_allocation_type
   - memtable_cleanup_threshold
   - file_cache_size_in_mb
   - memtable_flush_queue_size
   - memtable_flush_writers
   - memtable_heap_space_in_mb
   - memtable_offheap_space_in_mb
   - column_index_size_in_kb
   - index_summary_capacity_in_mb
   - index_summary_resize_interval_in_minutes
   - reduce_cache_capacity_to
   - reduce_cache_sizes_at
   - stream_throughput_outbound_megabits_per_sec
   - inter_dc_stream_throughput_outbound_megabits_per_sec
   - trickle_fsync
   - trickle_fsync_interval_in_kb
   - auto_bootstrap
   - batch_size_warn_threshold_in_kb
   - broadcast_address
   - initial_token
   - initial_token
   - num_tokens
   - partitioner
   - key_cache_keys_to_save
   - key_cache_save_period
   - key_cache_size_in_mb
   - row_cache_keys_to_save
   - row_cache_size_in_mb
   - row_cache_save_period
   - memory_allocator
   - counter_cache_size_in_mb
   - counter_cache_save_period
   - counter_cache_keys_to_save
   - counter_cache_keys_to_save
   - tombstone_warn_threshold
   - tombstone_failure_threshold
   - range_request_timeout_in_ms
   - read_request_timeout_in_ms
   - counter_write_request_timeout_in_ms
   - cas_contention_timeout_in_ms
   - truncate_request_timeout_in_ms
   - write_request_timeout_in_ms
   - request_timeout_in_ms
   - cross_node_timeout
   - internode_send_buff_size_in_bytes
   - internode_recv_buff_size_in_bytes
   - internode_compression
   - inter_dc_tcp_nodelay
   - streaming_socket_timeout_in_ms
   - native_transport_max_threads
   - native_transport_max_frame_size_in_mb
   - broadcast_rpc_address
   - rpc_keepalive
   - rpc_max_threads
   - rpc_min_threads
   - rpc_recv_buff_size_in_bytes
   - rpc_send_buff_size_in_bytes
   - rpc_server_type
   - dynamic_snitch_badness_threshold
   - dynamic_snitch_reset_interval_in_ms
   - dynamic_snitch_update_interval_in_ms
   - hinted_handoff_enabled
   - hinted_handoff_throttle_in_kb
   - max_hint_window_in_ms
   - max_hints_delivery_threads
   - batchlog_replay_throttle_in_kb
   - request_scheduler
   - request_scheduler_id
   - request_scheduler_options
   - thrift_framed_transport_size_in_mb
   - thrift_max_message_length_in_mb
   - permissions_validity_in_ms
   - permissions_update_interval_in_ms

Non-configurable properties with updated default values:

   - *authenticator*: **org.apache.cassandra.auth.PasswordAuthenticator**
   - *authorizer*: **org.apache.cassandra.auth.CassandraAuthorizer**
   - *snapshot_before_compaction*: **false**
   - *auto_snapshot*: **false**
   - *rpc_address*: **(controlled-by guestagent)**
   - *broadcast_rpc_address*: **(controlled-by guestagent)**
   - *listen_address*: **(controlled-by guestagent)**
   - *seed_provider.parameters.seeds*: **(controlled-by guestagent)**

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

1. Implement functionality to handle (read/write/update) YAML files.
2. Implement configuration-related manager API calls.

Upgrade Implications
====================

None

Dependencies
============

The patch set will be building on functionality implemented in blueprint:
cassandra-database-user-functions

Testing
=======

Unittests will be added to validate implemented functions and non-trivial
codepaths.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] Documentation on Cassandra 2.1: http://docs.datastax.com/en/cassandra/2.1/cassandra/gettingStartedCassandraIntro.html
.. [2] Documentation on Cassandra 2.1 configuration properties: http://docs.datastax.com/en/cassandra/2.1/cassandra/configuration/configTOC.html
