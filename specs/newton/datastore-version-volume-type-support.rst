..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

=========================================
Limit volume types for database instances
=========================================

Different volume types have different cost and performance
characteristics. Operators would like the flexibility to limit
specific databases to specific volume types similar to the way in
which databases can be limited to specific Nova flavors.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/associate-volume-type-datastore


Problem Description
===================

Operators can create different volume types and a user can specify a
volume type on a create instance request. Operators would like the
ability to limit the volume types that can be used for a specific
datastore-version in the same way that they can limit Nova flavors.

Proposed Change
===============

The implentation that associated flavors with datastores [1][2]
created a generic framework that provided for the specification of
datastore-version-metadata. This metadata was stored into a table in
the database called datastore_version_metadata.

.. code-block:: sql

     CREATE TABLE `datastore_version_metadata` (
                  `id` varchar(36) NOT NULL,
                  `datastore_version_id` varchar(36) DEFAULT NULL,
                  `key` varchar(128) NOT NULL,
                  `value` varchar(128) DEFAULT NULL,
                  `created` datetime NOT NULL,
                  `deleted` tinyint(1) NOT NULL,
                  `deleted_at` datetime DEFAULT NULL,
                  `updated_at` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `UQ_datastore_version_metadata_datastore_version_id_key_value` (
                  `datastore_version_id`,`key`,`value`),
    CONSTRAINT `datastore_version_metadata_ibfk_1`
    FOREIGN KEY (`datastore_version_id`)
    REFERENCES `datastore_versions` (`id`)
    ON DELETE CASCADE)

    CREATE TABLE `datastore_versions` (
                 `id` varchar(36) NOT NULL,
                 `datastore_id` varchar(36) DEFAULT NULL,
                 `name` varchar(255) DEFAULT NULL,
                 `image_id` varchar(36) NOT NULL,
                 `packages` varchar(511) DEFAULT NULL,
                 `active` tinyint(1) NOT NULL,
                 `manager` varchar(255) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `ds_versions` (`datastore_id`,`name`),
    CONSTRAINT `datastore_versions_ibfk_1`
    FOREIGN KEY (`datastore_id`)
    REFERENCES `datastores` (`id`))

    CREATE TABLE `datastores` (
                 `id` varchar(36) NOT NULL,
                 `name` varchar(255) DEFAULT NULL,
                 `default_version_id` varchar(36) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`))

The code populates flavor to datastore-version mappings by using a key
of 'flavor' in the table datastore_version_metadata. We propose to
extend this capability by using a key of 'volume-type' in the same
table.

We extend the trove-manage command and provide two new commands to add
and delete a volume-type mapping. In addition it is proposed that two
new commands be added to list existing associations. These list
commands will exploit an existing method (list datastore version
flavor associations).

Changes will be made to add a new mapping, see the section below on
Public API for details. The endpoint will provide a list of all
volume types allowed for a given tenant_id, datastore, and datastore
version.

Suitable error messages will be provided by adding new exception
classes. One error will be for a missing mapping between a given
datastore-version and a volume-type, and the other will be for a
situation where a mapping already exists.

The datastore version metadata model (trove/datastore/models.py) has
code for handling the existing flavor mappings. This code will be
refactored to extend the metadata mappings to also support volume
type.

The service class that will be referenced in the WSGI endpoint will be
added.

As we will be extending the existing metadata capability, no new
database tables will be required.

During instance creation, a check will be added for the volme type
being specified. If the volume type provided is not found to be a
valid volume type for the specified datastore version, an error will
be reported.

Currently volume type support does not extend to the cluster create
API.

Since this change will return volume type information, service, model
and view for VolumeType and VolumeTypes will be added.

If no datastore/version/volume-type has been configured then all
volume-types known to cinder are allowed.

A python-troveclient command to list datastore/version/volume-type
associations will be provided. It will call the new public API and show
the results.

A trove-manage command to list datastore/version/volume-type
associations will be provided. It will list only the associations in
the database and not intersect with valid cinder volume-types.

The trove-manage command performs no validations, it does not check
with cinder whether a volume-type being specified is actually a
volume-type known to cinder or not. And the volume-type, once defined
in trove could be deleted by cinder at a later time. It is therefore
possible that the volume type association in the trove metadata table
could become stale. Therefore, the implementation relies on the
concept of defined mappings and allowed mappings.

A defined mapping is something specified by the user in the metadata
table. An allowed mapping is the intersection of the defined mapping
and valid cinder volume types.

If a datastore does not support volumes, all of the checking described
in this specification is moot.

When the user has defined mappings for a particular datastore and
version, (and volume support is enabled), we look to see whether any
allowed mappings exist. If not, a distinct error message is generated
indicating that no valid volume types could be found.

If there are defined volume types, we ensure that volume type is
specified and is one of the allowed volume types.

New APIs will also be added to list all volume types available in cinder
and also to show the details of a specified volume type.

Tests will be added to exercise the new code paths.

Issues
------

1. In the present flavor implementation (that is used as the template
   for this volume_type) implementation, there is a discrepancy
   between the values returned by the
   list_datastore_version_flavor_associations (datastore/models.py)
   method, and the flavors that will be accepted in the check found in
   the create() call.

   This has been addressed in the code for volume type by instead
   calling the datastore/models method to list valid volume type
   associations.

2. The volume type was never stored with the instance and therefore
   when you show an instance, you can't tell what volume_type was
   specified on create.

3. volume_type is not required in the create call. If an association
   is present for datastore/version/volume_type and no volume_type is
   specified for the create, then the cinder default is used. The
   option would be to make the volume_type required which would be a
   change to the API.

   As implemented, if a volume_type is specified in create, it must be
   in the list of allowed volume types. Guessing the volume type is
   the alternative, and if more than one is allowed, a default would
   have to be provided. This has not been implemented.

Configuration
-------------

None

Database
--------

No database changes will be required.

Public API
----------

This change will add the following Public APIs:

List all volume types
.....................

This API will return all volume types as reported by cinder.

Request::

    GET /{tenant_id}/volume-types

Response::

    {
        "volume_types": [
            {
                "is_public": true,
                "description": "Example volume type",
                "id": <id>,
                "name": "example_volume_type"
            }
        ]
    }

Show volume type details
........................

This API will return the specified volume type's details as reported by
cinder.

Request::

    GET /{tenant_id}/volume-types/{id}

Response::

    {
        "volume_type": {
            "is_public": true,
            "description": null,
            "id": "53c71e3d-ef8f-4967-8b16-8a0ee6380d66",
            "name": "lvmdriver-1"
        }
    }


List allowed datastore version volume types
...........................................

This API will return all supported volume-types for the given
combination of tenant_id, datastore, and datastore vesion. If no association
has been configured then all volume types known to cinder are returned.

Request::

    GET /{tenant_id}/datastores/{datastore}/versions/{version_id}/volume-types

Response::

    {
        "volume_types": [
            {
                "is_public": true,
                "description": "Example volume type",
                "id": <id>,
                "name": "example_volume_type"
            }
        ]
    }


Public API Security
-------------------

There are no API security issues associated with this change.

Python API
----------

No changes.

CLI (python-troveclient)
------------------------

The trove-manage command will be the only affected as described above.

Internal API
------------

None.

Guest Agent
-----------

None

Alternatives
------------

One alternative that was considered was to associate datastores with
supported volume types (not datastore-versions). This would have
resulted in almost completely reimplementing the metadata linking
scheme that was created for flavors.


Dashboard Impact (UX)
=====================

The create dialog volume type dropdown will be filtered to show only valid
values based on the selected datastore version.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
   mvandijk

Milestones
----------

Target Milestone for completion:
     N-Release-1

Work Items
----------

   As described above in detail in the "Proposed Change" section.

Upgrade Implications
====================

There are no upgrade implications. We aren't adding or changing the
structure of any existing tables. The existing code can't create
mappings that could conflict with this proposed feature (all existing
code creates mappings with a key of 'flavor').

Dependencies
============

None

Testing
=======

New tests will be added.


Documentation Impact
====================

Yes, documentation of the mechanism to add, delete and list mappings will be
provided.


References
==========

.. [1] http://specs.openstack.org/openstack/trove-specs/specs/kilo/associate-flavors-datastores.html

.. [2] https://review.openstack.org/#/c/109824/


Appendix
========

None
