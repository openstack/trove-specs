..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

=============================
CouchDB Configuration Groups
=============================

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/couchdb-configuration-groups

Problem Description
===================

The CouchDB datastore currently does not support configuration groups.

Proposed Change
===============

The patch set will implement configuration groups for CouchDB.

CouchDB stores its configuration in 'local.ini' file.

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
   * configuration-detach

Guest Agent
-----------

* Implement *update_overrides* and *apply_overrides* in
  the *manager* and *service* modules.
* A configuration template and validation rules with changes noted in
  `Available Configuration Properties`_ will be provided.

The existing 'IniCodec' implementation will be reused to handle
text-file operations.


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

Sonali Goyal <sonaligoyal654321@gmail.com>
Victoria Martinez de la Cruz <victoria@redhat.com>

Milestones
----------

Netwon-1

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

The patch set will be building on functionality implemented in blueprint:
couchdb-database-user-functions


Testing
=======

The change is largely covered by the existing configuration tests.
Unit tests will be added to validate any CouchDB-specific codepaths.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] Documentation on CouchDB configuration: http://docs.couchdb.org/en/stable/config/index.html

Appendix
========

Available Configuration Properties
----------------------------------

The properties configurable by the user via the Trove API:
   [attachments]
   - compressible_types
   - compression_level
   [couchdb]
   - delayed_commits
   - max_attachment_chunk_size
   - attachment_stream_buffer_size
   - max_dbs_open
   - max_document_size
   - os_process_timeout
   [daemons]
   - auth_cache
   - db_update_notifier
   - external_manager
   - httpd
   - httpsd
   - query_servers
   - stats_aggregator
   - stats_collector
   - uuids
   - view_manager
   - vhosts
   [httpd]
   - allow_jsonp
   - authentication_handlers
   - changes_timeout
   - config_whitelist
   - default_handler
   - enable_cors
   - log_max_chunk_size
   - redirect_vhost_handler
   - secure_rewrites
   - server_options
   - socket_options
   - vhost_global_handlers
   - x_forwarded_host
   - x_forwarded_proto
   - x_forwarded_ssl
   [replicator]
   - checkpoint_interval
   - connection_timeout
   - db
   - http_connections
   - max_replication_retry_count
   - retries_per_request
   - socket_options
   - ssl_certificate_max_depth
   - ssl_trusted_certificates_file
   - use_checkpoints
   - verify_ssl_certificates
   - worker_batch_size
   - worker_processes
   [query_server_config]
   - commit_freq
   - os_process_limit
   - reduce_limit
   [os_daemon_settings]
   - max_retries
   - retry_time
   [couch_httpd_auth]
   - allow_persistent_cookies
   - auth_cache_size
   - authentication_db
   - authentication_redirect
   - iterations
   - max_iterations
   - min_iterations
   - proxy_use_secret
   - public_fields
   - require_valid_user
   - secret
   - timeout
   - users_db_public
   - x_auth_roles
   - x_auth_token
   - x_auth_username
   - use_users_db
   [compaction_daemon]
   - check_interval
   - min_file_size
   [database_compaction]
   - doc_buffer_size
   - checkpoint_after
   [log]
   - include_sasl
   - level
   [view_compaction]
   - keyvalue_buffer_size

Guestagent-controlled properties:

   [httpd]
   - port
   - bind_address
   [log]
   - file
   [couchdb]
   - uri_file
   - util_driver_dir
   - view_index_dir
   - database_dir

