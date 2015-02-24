..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode
..

=======================
 Datastore Visibility
=======================

Launchpad blueprint:

https://blueprints.launchpad.net/trove/+spec/datastore-visibility

Motivation: Since Trove supports multiple datastore types, there is a
need for Trove to have a greater control over the customer visibility
of these datastore types. This change enables Trove to control the
visibility of the various datastore types.

Problem Description
===================

There might be some datastore types, which the deployers require to be
active but not visible to customers in the production environment.
Example use case: Say we want to have an active datastore A in production
and not expose it to customers yet.

Proposed Change
===============

This change suggests adding a visibility attribute to the datastore
versions. This enables the datastore to still be active, but not visible
to the users.
The visibility flag will ensure it is visible on the datastore list
call only to admins.

1. Visibility attribute to the datastore version. It can be:
   public/private/unlisted/deprecated.
2. Adding a datastore version members table to add tenants for
   private datastores.
3. If visibility is public:

   - All users can view it in the list.

   - All users can make a GET call on the datastore version.

   - All admin can view it in the list.

   - All admin can make a GET call on the datastore version.

4. If visibility is private:

   - Members only can view it in the list.

   - Members only can make a GET call on the datastore version.

   - All admin can view it in the list.

   - All admin can make a GET call on the datastore version.

   - All admin can add and remove tenants as members of a datastore version.

5. If visibility is unlisted:

   - All users can make a GET call on the datastore version.

   - All admin can view it in the list.

   - All admin can make a GET call on the datastore version.

6. If visibility is deprecated:

   - All admin can view it in the list.

   - All admin can make a GET call on the datastore version.

   - Only admins can create a 'deprecated' instance.


Configuration
-------------

None

Database
--------

1. Database migration of adding a column 'visibility' to the
   datastore_versions table.

Table datastore_versions::

    Field          | Type        | Null | Key     | Default | Extra|
    ---------------------------------------------------------------|
    id             | varchar(36) | NO   | PRIMARY | NULL    |      |
    datastore_id   | varchar(36) | YES  | MUL     | NULL    |      |
    name           | varchar(255)| YES  |         | NULL    |      |
    image_id       | varchar(36) | NO   |         | NULL    |      |
    packages       | varchar(511)| YES  |         | NULL    |      |
    active         | tinyint(1)  | NO   |         | NULL    |      |
    manager        | varchar(255)| YES  |         | NULL    |      |
    visibility     | varchar(255)| NO   |         | public  |      |

2. New table datastore_version_members which consists of columns - id,
   datastore_version_id,tenant_id.

Table datastore_version_members::

    Field               | Type        | Null | Key         | Default | Extra|
    ------------------------------------------------------------------------|
    id                  | varchar(36) | NO   | PRIMARY     | NULL    |      |
    datastore_version_id| varchar(36) | YES  | Foreign [1] | NULL    |      |
    tenant_id           | varchar(36) | NO   |             | NULL    |      |

    [1] datastore_version_id is a Foreign-Key on datastore_version.id

Public API
----------

Admin calls related to datastore versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Set visibility

   POST /{tenant_id}/mgmt/datastores/{datastore}/versions/{id}

   Request::

    {
        "datastore_version":{
            "visibility":"<visibility value>"
        }
    }


2. Get datastore version - A visibility field added only for admin users.

   GET /{tenant_id}/datastores/{datastore_id}/versions/{id}

   Response::

    {
        "version":{
            "active":true,
            "datastore":"9dd70f56-72e9-444b-9881-f564ac955056",
            "id":"65747630-1ce7-4be0-92d4-8695825a475b",
            "image":"32070be9-3cab-4cee-be05-524b4f379447",
            "links":[
                {
                    "href":"https://172.16.117.178:8779/v1.0/9a4e7142f34b4ce990a276c82b7beb15/datastores/versions/65747630-1ce7-4be0-92d4-8695825a475b",
                    "rel":"self"
                },
                {
                    "href":"https://172.16.117.178:8779/datastores/versions/65747630-1ce7-4be0-92d4-8695825a475b",
                    "rel":"bookmark"
                }
            ],
            "name":"5.5",
            "packages":"mysql-server-5.5",
            "visibility":"public"
        }
    }

Admin calls related to datastore version members
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add a member:

   POST /{tenant_id}/mgmt/datastores/{datastore}/versions/{id}/members

   Request::

    {
        "member":"<TENANT_ID>"
    }


2. Delete a member:

  DELETE
  /{tenant_id}/mgmt/datastores/{datastore}/versions/{id}/members/{member_id}


3. Get a member:

   GET
   /{tenant_id}/mgmt/datastores/{datastore}/versions/{id}/members/{member_id}

   Response::

    {
       "datastore_version_member":{
          "id":"<MEMBER_ID>",
          "datastore_version_id":"<DATASTORE_VERSION_ID>",
          "member":"<TENANT_ID>"
        }
    }


4. List members for a datastore version

  GET  /{tenant_id}/mgmt/datastores/{datastore}/versions/{id}/members

  Response::

    {
       "datastore_version_members":[
            {
                "id":"<MEMBER_ID>",
                "datastore_version_id":"<DATASTORE_VERSION_ID>",
                "member":"<TENANT_ID>"
            },
            {
                "id":"<MEMBER_ID>",
                "datastore_version_id":"<DATASTORE_VERSION_ID>",
                "member":"<TENANT_ID>"
            }
        ]
    }


5. Get members by tenant id:

   GET /{tenant_id}/mgmt/datastores/{datastore}/versions/members/{tenant_id}

   Response::

    {
       "datastore_version_members":[
          {
             "id":"<MEMBER_ID>",
             "datastore_version_id":"<DATASTORE_VERSION_ID>",
             "member":"<TENANT_ID>"
          },
          {
             "id":"<MEMBER_ID>",
             "datastore_version_id":"<DATASTORE_VERSION_ID>",
             "member":"<TENANT_ID>"
          }
       ]
    }

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

Primary:
 - Launchpad: riddhi89
 - IRC: Riddhi
 - Email: ridhi.j.shah@gmail.com
Co-Authored by:
  - Theron Voran
  - Email: theron.voran@rackspace.com

Milestones
----------

Kilo-1
Kilo-2

Work Items
----------

Already in review process - References [1].

Implementation
---------------

It is in the process of review - References [1].


Dependencies
============

None


Testing
=======

Unit tests, fake tests and real mode tests.


Documentation Impact
====================

Since API calls have been added/modified, their respective samples
would need to be incorporated in the API docs.


References
==========

1. https://review.openstack.org/#/c/110197/
