..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================
Datastore Registration API
==========================

Blueprint:

https://blueprints.launchpad.net/trove/+spec/datastore-registration-api

The proposal is to introduce a new Management API that facilitates a
the datastore registration on an existing Trove Deployment

Problem Description
===================

Today, the only means of adding/registering a datastore/datastore-version on
an existing deployment is to use some sequence of trove-manage
(datastore_update, datastore_version_update) to add a datastore followed by
adding the datastore-version with its image.

Another problem with this process is one needs to have access to the
trove-api server from where one can execute trove-manage, alteratively
one needs direct access to database if the want to by-pass trove-manage
and add the entries by using an insert/update command to tables, both of
these methods requires to relax the security of trove-api/database server
for direct access to operator/deployer.

One more problem that lies with registering datastores is we need to
use multiple commands to register a new datastore with an image-id.

Use Cases
----------

* As a deployer, I want to be able to add new datastores through the
  Trove management API, without having to log in to the Trove control plane
  and manually running a trove-manage command.

Proposed Change
===============

Following functionalities would be added as part of the change::
    - Add/register a new datastore version.
    - Get a list of datastore-versions.
    - Get information about an existing datastore-version.
    - Update image/manager/packages/active/default for an existing datastore version.
    - Delete an existing datastore version.

While registering a datastore version, we would create a datastore with
the requested datastore_name, if it does not exists.

These functionalities would only be available to an admin user
who would access the APIs via an admin tenant.

Configuration
-------------

No Configuration changes.

Database
--------

No Database changes.

Public API
----------

No public API changes.


Public API Security
-------------------

None


Python API
----------

None


CLI (python-troveclient)
------------------------

None


Management API
--------------

The request/response for new APIs are as follows.
These APIs would be invokable only through an admin tenant.


------------------------------
Add/Register Datastore Version
------------------------------

Request::

    POST /v1.0/<tenant_id>/mgmt/datastore-versions
    {
      "version": {
        "datastore": "mysql",
        "name": "5.6",
        "manager": "mysql",
        "image": "154b350d-4d86-4214-9067-9c54b230c0da",
        "packages": ["mysql-server-5.6"],
        "active": true,
        "default": true,
        }
    }

Response::

    {
    }

HTTP Codes::

    202 - Accepted.
    400 - Bad Request. Datastore Version Already Exists.
    404 - Not Found. Image not found.


----------------------
Get Datastore Versions
----------------------

Request::

    GET /v1.0/<tenant_id>/mgmt/datastore-versions

Response::

    {
        "versions": [
          {
            "datastore_id": "b80c2b43-cd87-4d5d-9f32-a4996bd57cb1",
            "datastore_name": "mysql",
            "id": "b8a23fa1-1faf-441a-a6b7-83a19c30f347",
            "name": "5.6",
            "manager": "mysql",
            "image": "154b350d-4d86-4214-9067-9c54b230c0da",
            "packages": ["mysql-server-5.6"],
            "active": true,
            "default": true,
          },
          {
            "datastore_id": "127bc577-8054-4b32-9ed3-2d6b01773810",
            "datastore_name": "vertica",
            "id": "21c8805a-a800-4bca-a192-3a5a2519044d",
            "name": "7.1",
            "manager": "vertica",
            "image": "6230baf1-dffe-40fa-a1fb-47d9ff346503",
            "packages": ["vertica-7.1"],
            "active": true,
            "default": true,
          }]
    }

HTTP Codes::

    200 - OK.


-----------------------------------------
Get information about a Datastore Version
-----------------------------------------

Request::

    GET /v1.0/<tenant_id>/mgmt/datastore-versions/<datastore_version_id>

Example::

    GET /v1.0/<tenant_id>/mgmt/datastore-versions/b8a23fa1-1faf-441a-a6b7-83a19c30f347

Response::

    {
        "version":
          {
            "datastore_id": "b80c2b43-cd87-4d5d-9f32-a4996bd57cb1",
            "datastore_name": "mysql",
            "id": "b8a23fa1-1faf-441a-a6b7-83a19c30f347",
            "name": "5.6",
            "manager": "mysql",
            "image": "154b350d-4d86-4214-9067-9c54b230c0da",
            "packages": ["mysql-server-5.6"],
            "active": true,
            "default": true,
          }
    }

HTTP Codes::

    200 - OK.
    404 - Not Found. Datastore Version not found.


--------------------------------------------------------------------
Update Image/Manager/Packages/Active/Default for a Datastore Version
--------------------------------------------------------------------

Request::

    PATCH /v1.0/<tenant_id>/mgmt/datastore-versions/<datastore_version_id>

    Payload for this request can be those attributes which one wants to update.

Example::

    PATCH /v1.0/<tenant_id>/mgmt/datastore-versions/b8a23fa1-1faf-441a-a6b7-83a19c30f347
    {
        "image": "e33f8e2f-1148-461c-a7ea-f8228e7c5f4a",
    }

Response::

    {
    }

HTTP Codes::

    202 - Accepted.
    404 - Not Found. Datastore Version not found.
    404 - Not Found. Image not found.


------------------------------------
Delete an existing Datastore Version
------------------------------------
Request::

    DELETE /v1.0/<tenant_id>/mgmt/datastore-versions/<datastore_versionid>

Example::

    DELETE /v1.0/<tenant_id>/mgmt/datastore-versions/b8a23fa1-1faf-441a-a6b7-83a19c30f347

Response::

    {
    }

HTTP codes::

    202 - Accepted.
    404 - Not Found. Datastore Version not found.
    409 - Conflict. Instance(s) exists for the datastore version.


Internal API
------------

No internal API changes.

Guest Agent
-----------

No Guest Agent changes.


Alternatives
------------

The current alternative is use trove-manage or use database directly,
but both these methods need relaxation on access-policies of api/db servers
which has its own security implications.


Implementation
==============

Assignee(s)
-----------

Sushil Kumar (skm.net@gmail.com)

Milestones
----------

Liberty-2

Work Items
----------

- Implement API routes
- Implement management API
- Implement unit-tests


Upgrade Implications
====================

None.


Dependencies
============

There is an ongoing work to associate flavors with
datastore versions(https://review.openstack.org/#/c/109824).

It has to be noted once we have these flavor-mappings in place,
there would be two available options while deleting a datastore-version:

- Don't delete datastore-version if it has any flavor-mappings.
- Delete the flavor-mappings along with the datastore-versions.


Testing
=======

Unit tests will be added to cover non-trivial code paths.


Documentation Impact
====================

Management API's documentation would be updated with new API.


References
==========

None.
