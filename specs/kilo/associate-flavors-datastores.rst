..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

..

============================================
 Associate instance flavors with datastores
============================================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/associate-flavors-datastores

Motivation:
Each datastore type has its own hardware requirements (minimum and
maximum). Currently, trove lacks the ability to enforce this
requirement. This change enables trove with the ability to associate
the virtual hardware templates (flavors) with datastore types.

Problem Description
===================

Trove supports multiple datastore types. However, each datastore type
has its own hardware requirements, which presently, cannot be enforced
in trove.

For example:
MySQL - Minimum System Requirements:
- 2 or more CPU cores
- 2 or more GB of RAM
- Disk I/O subsystem applicable for a write-intensive database

Find more information about other datastore specific hardware
requirements in the References section.


Trove uses virtual hardware templates called 'flavors' in
OpenStack. In order for trove to be able to enforce the datastore
specific hardware requirements, there needs to be a way in which
datastore types can be associated with their minimum flavor (hardware)
requirements. This way, the user/administrator can at least be
notified while provisioning the datastore with the inappropriate
flavor, that does not meet the minimum hardware requirements.


Proposed Change
===============

- The trove-manage utility will provide the ability to add and delete
  the datastore version-flavor associations.
- There will be an additional API call in order to get a list of
  flavors for the specified datastore version id.


Configuration
-------------

None

Database
--------
No impact on existing tables.

One new entity will be created in the trove database:
datastore_version_metadata. This will store any additional metadata
related to a datastore version including its relation with flavors:
key=flavor and the value=flavor_id.

The blueprint specifies the table attributes in detail.

Public API
----------

Does not impact any other API which the user has access to.

Public API Security
-------------------

None

Internal API
------------

None

Guest Agent
-----------

None


Alternatives
------------

None


Implementation
==============

Assignee(s)
-----------

 - Launchpad: riddhi89
 - IRC: Riddhi
 - Email: ridhi.j.shah@gmail.com

Milestones
----------

Kilo-1

Work Items
----------

- Add the new database schema for datastore version metadata.
- trove-manage util extension to associate a flavor list with a
  datastore version id
- trove-manage util extension to delete a flavor associated with a
  datastore version id.
- REST API call to list flavors for a datastore version id
  (/{tenant_id}/flavors/{datastore_version_id})
- Unit and integration tests


Dependencies
============

None

Testing
=======

- Unit tests for individual components.
- Integration tests for end-to-end testing.


Documentation Impact
====================

- New API call to list flavors given a datastore version id.
- trove-manage util extensions to add/delete datastore version -
  flavor associations.


References
==========

* Further hardware requirements for different datastore types:
  https://wiki.openstack.org/wiki/TroveFlavorsPerDatastore
