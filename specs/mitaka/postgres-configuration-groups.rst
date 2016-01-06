..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

=============================
Postgres Configuration Groups
=============================

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/postgres-configuration-groups

Problem Description
===================

The Postgres guestagent currently does not support configuration groups.

Proposed Change
===============

The patch set will implement configuration groups for Postgres 9.3 or above.

Postgres stores its configuration [1]_ in 'postgresql.conf' file.
Configuration directives have key-value format:
"keyword = value"

In addition to the 'postgresql.conf' file already mentioned,
PostgreSQL uses two other configuration files
('pg_hba.conf' and 'pg_ident.conf'), which control client authentication.

These will be written directly by the guest-agent and will not
be exposed via the configuration groups mechanism.

Configuration changes can be loaded on the fly without interrupting
any open connections by the special 'pg_reload_conf' call [2]_.
Note that Postgres also has a 'SET' command, but it only affects the current
session values.

Most configuration properties will be available via configuration groups.
Some, however, do not make sense in the Trove context.

These include (will be documented in the configuration template):

   - guestagent specific (e.g. file paths, passwords, file access rules)
   - items that Trove needs to control (replication/clustering/log properties)

See `Available Configuration Properties`_ for the full list of supported
options.

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

* Implement *update_overrides* and *apply_overrides* in
  the *manager* and *service* modules.
* A configuration template and validation rules will with changes noted in
  `Available Configuration Properties`_ will be provided.

The existing 'PropertiesCodec' implementation will be reused to handle
text-file operations.
Configuration overrides will be implemented using the 'OneFileOverrideStrategy'
of the guestagent configuration manager.

Alternatives
------------

None


Dashboard Impact (UX)
=====================

TBD (section added after approval)


Implementation
==============

Assignee(s)
-----------

Petr Malik <pmalik@tesora.com>

Milestones
----------

Mitaka

Work Items
----------

All changes will be done in the context of a single task.

1. Implement configuration-related manager API calls:

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

The change is largely covered by the existing configuration tests.
Unit tests will be added to validate any Postgres-specific codepaths.
A 'postgres_helper' will be contributed to the scenario tests to
enable configuration coverage on this datastore.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] Documentation on Postgres configuration: http://www.postgresql.org/docs/9.3/static/runtime-config.html
.. [2] Notes on Postgres system administration functions: http://www.postgresql.org/docs/9.3/static/functions-admin.html

Appendix
========

Available Configuration Properties
----------------------------------

The properties configurable by the user via the Trove API:

   - max_connections
   - superuser_reserved_connections
   - bonjour
   - bonjour_name
   - authentication_timeout
   - password_encryption
   - db_user_namespace
   - tcp_keepalives_idle
   - tcp_keepalives_interval
   - tcp_keepalives_count
   - shared_buffers
   - huge_pages
   - temp_buffers
   - max_prepared_transactions
   - work_mem
   - maintenance_work_mem
   - autovacuum_work_mem
   - max_stack_depth
   - dynamic_shared_memory_type
   - temp_file_limit
   - max_files_per_process
   - vacuum_cost_delay
   - vacuum_cost_page_hit
   - vacuum_cost_page_miss
   - vacuum_cost_page_dirty
   - vacuum_cost_limit
   - bgwriter_delay
   - bgwriter_lru_maxpages
   - bgwriter_lru_multiplier
   - effective_io_concurrency
   - max_worker_processes
   - fsync
   - synchronous_commit
   - wal_sync_method
   - full_page_writes
   - wal_log_hints
   - wal_buffers
   - wal_writer_delay
   - commit_delay
   - commit_siblings
   - checkpoint_segments
   - checkpoint_timeout
   - checkpoint_completion_target
   - checkpoint_warning
   - wal_keep_segments
   - wal_sender_timeout
   - synchronous_standby_names
   - vacuum_defer_cleanup_age
   - hot_standby
   - max_standby_archive_delay
   - max_standby_streaming_delay
   - wal_receiver_status_interval
   - hot_standby_feedback
   - wal_receiver_timeout
   - enable_bitmapscan
   - enable_hashagg
   - enable_hashjoin
   - enable_indexscan
   - enable_indexonlyscan
   - enable_material
   - enable_mergejoin
   - enable_nestloop
   - enable_seqscan
   - enable_sort
   - enable_tidscan
   - seq_page_cost
   - random_page_cost
   - cpu_tuple_cost
   - cpu_index_tuple_cost
   - cpu_operator_cost
   - effective_cache_size
   - geqo
   - geqo_threshold
   - geqo_effort
   - geqo_pool_size
   - geqo_generations
   - geqo_selection_bias
   - geqo_seed
   - default_statistics_target
   - constraint_exclusion
   - cursor_tuple_fraction
   - from_collapse_limit
   - join_collapse_limit
   - log_truncate_on_rotation
   - log_rotation_age
   - log_rotation_size
   - client_min_messages
   - log_min_messages
   - log_min_error_statement
   - log_min_duration_statement
   - debug_print_parse
   - debug_print_rewritten
   - debug_print_plan
   - debug_pretty_print
   - log_checkpoints
   - log_connections
   - log_disconnections
   - log_duration
   - log_error_verbosity
   - log_hostname
   - log_line_prefix
   - log_lock_waits
   - log_statement
   - log_temp_files
   - log_timezone
   - track_activities
   - track_counts
   - track_io_timing
   - track_functions
   - track_activity_query_size
   - log_parser_stats
   - log_planner_stats
   - log_executor_stats
   - log_statement_stats
   - autovacuum
   - log_autovacuum_min_duration
   - autovacuum_max_workers
   - autovacuum_naptime
   - autovacuum_vacuum_threshold
   - autovacuum_analyze_threshold
   - autovacuum_vacuum_scale_factor
   - autovacuum_analyze_scale_factor
   - autovacuum_freeze_max_age
   - autovacuum_multixact_freeze_max_age
   - autovacuum_vacuum_cost_delay
   - autovacuum_vacuum_cost_limit
   - search_path
   - default_tablespace
   - temp_tablespaces
   - check_function_bodies
   - default_transaction_isolation
   - default_transaction_read_only
   - default_transaction_deferrable
   - session_replication_role
   - statement_timeout
   - lock_timeout
   - vacuum_freeze_min_age
   - vacuum_freeze_table_age
   - vacuum_multixact_freeze_min_age
   - vacuum_multixact_freeze_table_age
   - bytea_output
   - xmlbinary
   - xmloption
   - datestyle
   - intervalstyle
   - timezone
   - timezone_abbreviations
   - extra_float_digits
   - client_encoding
   - lc_messages
   - lc_monetary
   - lc_numeric
   - lc_time
   - default_text_search_config
   - deadlock_timeout
   - max_locks_per_transaction
   - max_pred_locks_per_transaction
   - array_nulls
   - backslash_quote
   - default_with_oids
   - escape_string_warning
   - lo_compat_privileges
   - quote_all_identifiers
   - sql_inheritance
   - standard_conforming_strings
   - synchronize_seqscans
   - transform_null_equals
   - exit_on_error
   - restart_after_crash

Guestagent-controlled properties:

   - data_directory
   - hba_file
   - ident_file
   - external_pid_file
   - listen_addresses
   - port
   - unix_socket_directories
   - unix_socket_group
   - unix_socket_permissions
   - wal_level
   - archive_mode
   - archive_command
   - archive_timeout
   - log_destination
   - logging_collector
   - log_directory
   - log_filename
   - log_file_mode
   - update_process_title
