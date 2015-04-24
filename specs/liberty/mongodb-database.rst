..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst


=============================
 MongoDB database management
=============================

https://blueprints.launchpad.net/trove/+spec/mongodb-database

Enable MongoDB database management functionality.


Problem description
===================

The MongoDB datastore does not support database management features. Allowing
the user to create, list, and delete databases through the API is essential.


Proposed change
===============

Three standard Trove commands will be enabled for MongoDB:

1. database-create
2. database-list
3. database-delete

The changes will be confined to the guestagent code. The taskmanager, API, and
conductor do not require any code changes. The code changes will be to
implement a new class service.MongoDBAdmin and the corresponding methods as
members of the class. The methods of manager.Manager will be updated to call
the admin functions.

Calls to MongoDB will be done in Python via the PyMongo library, which is
required to be pre-installed on the guest.


Configuration
-------------

No changes will be made to any configuration files.


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

    trove/guestagent/db/models.py - add a MongoDBSchema class.
    trove/guestagent/datastore/experimental/mongodb/manager.py - enable functions.
    trove/guestagent/datastore/experimental/mongodb/service.py - add functions.

The Guest Agent will be changed to support the following manager functions:

1. create_database - MongoDB does not have a method to explicitly create a
   database. The database to use is specified via 'use <dbname>', but this does
   not create the database. Databases are created when a 'document' is first
   inserted into them. To ensure a database is created, a dummy document will
   be inserted but then deleted.

2. list_databases - Run 'pymongo.MongoClient.database_names()' and return the resulting list.

3. delete_database - Drop the database with
   'pymongo.MongoClient.drop_database("<dbname>")'. Users associated with the
   database will have to be removed manually.


Alternatives
------------

create_database could not create a dummy object in the database.


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

The changes will be implemented in a single commit. The scope is small and the
functionality is linked.


Upgrade Implications
====================

There will be no upgrade implications.


Dependencies
============

There are no dependencies on other work in progress.


Testing
=======

Unit tests will be added to validate non-trivial code paths.
Integration tests may be added as needed.

Documentation Impact
====================

The MongoDB datastore documentation can be updated to reflect the enabled
features.


References
==========

There are no external references in this document.
