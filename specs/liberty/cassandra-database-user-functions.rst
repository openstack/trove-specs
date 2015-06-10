..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst

=====================================
Cassandra Database and User Functions
=====================================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/cassandra-database-user-functions

Problem Description
===================

The Cassandra datastore currently does not support keyspace [*]_ and
user management features.

.. [*] A keyspace is the outermost container for data in Cassandra,
       corresponding closely to a relational database.

Proposed Change
===============

The patch set will implement the following keyspace and user related
functionality for Cassandra 2.1 datastore:

User Functions:

- create/delete/get user
- list users
- change password
- grant/revoke/list access
- update attributes

Keyspace Functions:

- create/delete database
- list databases

Configuration
-------------

Cassandra stores its configuration in 'cassandra.yaml' file
(commonly in '/etc/cassandra').
The node (datastore service) has to be restarted for any changes to the
configuration file to take effect.
The configuration template will have to be updated to enable authentication and
authorization in order to support datastore users and related functions.
Client-specific settings (authentication defaults) are stored in
'~/.cassandra/cqlshrc' where '~' is the home directory of the Trove user.

Database
--------

None

Public API
----------

None

Public API Security
-------------------

The current implementation allows original anonymous connections therefore
making the datastore wide open for anybody with connection URL.
This has to be changed first as the user functions are not even enabled in this
setting.

In Cassandra only SUPERUSERS can create other users and
grant permissions to database resources.
Trove uses the 'cassandra' superuser to perform its administrative
tasks.
The users it creates are all 'normal' (NOSUPERUSER) accounts.
The permissions it can grant are also limited to non-superuser
operations. This is to prevent anybody from creating a new superuser via
the Trove API.
Similarly, all list operations include only non-superuser accounts.
Updatable attributes include username and password.
We are not going to implement enabling superuser account in this patch set.

The datastore configuration template had to be updated to enable authentication
and authorization support (original configuration allowed anonymous
connections). Default implementations used are:

* *authenticator: org.apache.cassandra.auth.PasswordAuthenticator*
* *authorizer: org.apache.cassandra.auth.CassandraAuthorizer*

The superuser password needs to be changed from the default 'cassandra'
to a random Trove password which is then stored in a Trove-read-only
file in '~/.cassandra/cqlshrc' which is also the default location for
client settings.

Internal API
------------

None

Guest Agent
-----------

The current implementation uses the CQLSH command line client to interface with
the underlying database. Trove talks to the CQLSH client via the available
shell and relies on parsing the output of the client to determine the current
state of the datastore and status of the last operation.
It also requires Trove to provide the input as a formatted
(and sanitized) string accepted by the installed version of the client.
This is not very portable and poses numerous potential compatibility issues in
the future when the guest agent gets ported to other platforms.
It also completely bypasses the native exception handling implemented by the
Python client.
In order to make the guestagent communicate via the native Python API and
avoid future portability issues we reimplement the communication interface
using the the official open-source Python driver for Cassandra.
The native interface will be implemented in CassandraConnection and
will also be used to obtain the database status leveraging Python exceptions
framework.

User-related functions require having the authorization and authentication
support enabled on the server. The configuration template will be updated to
reflect this requirement (see the section on 'Public API Security').

The following section elaborates on keyspace *("database")* functions.
Cassandra natively supports row replication. It can store a configurable number
of copies (replicas) of each row on multiple nodes to ensure reliability and
fault tolerance. All such replicas are equally important;
there is no primary or master.
It supports several replication strategies which determine how the replicated
rows get distributed across the entire Cassandra cluster.
The total number of row replicas in a cluster is referred to as the
replication factor.
The 'create database' implementation will be using 'SimpleStrategy'
which is the only strategy that makes sense for a single node setup.
It is a very simplistic configuration with just a single copy (replica) on
the guest machine only good for the most basic
applications and demonstration purposes.
The following system keyspaces will be by-default excluded from database
operations and listing by having them included in the 'ignore_dbs' list:
'system', 'system_auth', 'system_traces'

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

Liberty-1

Work Items
----------

1. Implement native-driver-based connection for Cassandra datastore.
2. Enable authentication and authorization on server.
3. Implement user-function API calls.

Upgrade Implications
====================

The required native Python driver 2.0.x supports Cassandra 1.2 and higher.

Dependencies
============

Trove uses the official open-source Python driver [1]_ for Cassandra
to connect to the database and execute queries.
The driver already exists in OpenStack global requirements.
It does not have to be included in the 'requirements.txt' file, but
it will need to be added to 'test-requirements.txt' file to enable unit tests.
The image provider will be required to install it ('cassandra-driver')
in the Cassandra images.
The current Trove integration images will be updated to do that.

Testing
=======

Unittests will be added to validate implemented functions and non-trivial
codepaths.

Documentation Impact
====================

The datastore documentation should be updated to reflect the enabled features.

References
==========

.. [1] Native Python Driver for Cassandra: http://docs.datastax.com/en/developer/python-driver/2.5/common/drivers/introduction/introArchOverview_c.html
.. [2] Documentation on Cassandra 2.1: http://docs.datastax.com/en/cassandra/2.1/cassandra/gettingStartedCassandraIntro.html
.. [3] CQL Reference: http://docs.datastax.com/en/cql/3.1/cql/cql_reference/cqlReferenceTOC.html
