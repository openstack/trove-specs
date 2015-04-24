..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst


==========================
 MongoDB users management
==========================

https://blueprints.launchpad.net/trove/+spec/mongodb-users

Enable MongoDB users management functionality.


Problem description
===================

The MongoDB guest agent does not support users management features. Allowing
the user to create, list, and delete users, enable/check root access, and
grant/revoke user access through the API is essential.

MongoDB users are unique to each database. A user is identified by both its name
and database. Therefore the Trove actions requiring user names need
the value to be in the following string format: "<database>.<username>".
MongoDB does not allow the following characters in the database name: /\. "$


Proposed change
===============

Calls to MongoDB will be done in Python via the PyMongo library, which is
required to be pre-installed on the guest.

Features
--------

A number of Trove commands will be enabled for the MongoDB datastore.
Also, MongoDB's authentication protocol will be enabled by default, making
the database secure.

Functions
~~~~~~~~~

Several standard Trove commands will be enabled for MongoDB. Below are the
corresponding CLI commands with all allowed arguments:

::

    user-create <instance> <database>.<name> <password>
    user-list <instance>
    user-delete <instance> <database>.<name>
    user-show <instance> <database>.<name>
    root-enable <instance>
    root-show <instance>
    user-grant-access <instance> <database>.<name> <access_databases>
    user-revoke-access <instance> <database>.<name> <access_database>
    user-show-access <instance> <database>.<name>

The code changes will be to implement a new class service.MongoAdmin and the
corresponding methods as members of the class. The methods of manager.Manager
will be updated to call the admin functions.


Security
~~~~~~~~

Currently the MongoDB datastore creates an insecure database. To make the
above functionality useful the guest agent's MongoDB server will be made
secure. This will be done by enabling authentication and creating a Trove
user 'os_admin' on the server by default. The Trove user will have user and
database administrator privileges, but not read/write. When the guest is first
started the guest agent will generate a password and
connect (because of the localhost exception) to the server. It will then run
the following (below is Mongo shell code, but it will be implemented using
PyMongo):

::

    use admin
    db.createUser(
        {
            user: "os_admin",
            pwd: "<generated_password>",
            roles: [
                { role: "userAdminAnyDatabase", db: "admin" },
                { role: "dbAdminAnyDatabase", db: "admin" },
                { role: "cluserAdmin", db: "admin" }
            ]
        }
    )

Authentication will be enabled by default. To disable it a configuration group
can be used with the option {'auth': 'false'}.

Note: enabling authentication on MongoDB effects clustering as shards are
required to use a shared key file to connect to each other. Therefore a new
cryptographically secure key will be generated during cluster-create to be used
by the shards. This key value will be pushed to each shard, where it will be
stored for connection use. The key will not be stored on the controller. The
controller will ask an existing cluster guest for the key when adding new
shards.


Configuration
-------------

The mongodb configuration file will have 'auth' set to 'on' to enable
authentication on the server.

A new MongoDB RC script will be created at ~/.mongorc.js. This file will store
the username and generated password, allowing the local MongoDB client to
automatically connect using those credentials.


Database
--------

No new items will be added here.


Public API
----------

No API changes.


Public API Security
-------------------

No API Security changes.


Internal API
------------

No Internal API changes.


Guest Agent
-----------

Modified files:

::

    trove/guestagent/db/models.py - add a MongoDBUser class.
    trove/guestagent/datastore/experimental/mongodb/manager.py - enable functions.
    trove/guestagent/datastore/experimental/mongodb/service.py - add functions.
    trove/guestagent/datastore/experimental/mongodb/system.py - store system constants.

The Guest Agent will be changed to support the following manager functions:

- create user - using 'createUser()'
- list users - query the admin database's system.users collection
- delete user - using 'dropUser()'
- show user - using 'getUser()'
- enable root - create user "root" and grant the role "root"
- check if root is enabled - check if user "root" exists
- grant user access to a database - using 'updateUser()'
- revoke user access to a database - using 'updateUser()'
- show user access to a database - using 'getUser()'


Alternatives
------------

Grant os_admin “root” role for full access.


Implementation
==============

Assignee(s)
-----------

Matthew Van Dijk


Milestones
----------

liberty-1


Work Items
----------

The work will be split into four deliverables:

1) Enable authentication on server
2) create/list/show/delete users
3) enable/check root
4) grant/show/revoke access


Upgrade Implications
====================

There will be no upgrade implications.


Dependencies
============

There are no dependencies on other work in progress.


Testing
=======

Unit tests will be added to validate non-trivial codepaths.
Integration tests may be added if necessary.


Documentation Impact
====================

Documentation will be required to explain that authentication is enabled on
MongoDB guests. The MongoDB datastore documentation can be updated to reflect
the enabled features.


References
==========

`MongoDB manual
<http://docs.mongodb.org/manual/>`_

