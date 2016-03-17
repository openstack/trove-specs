..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

..
    This template should be in ReSTructured text. The filename in the git
    repository should match the launchpad URL, for example a URL of
    https://blueprints.launchpad.net/trove/+spec/awesome-thing should be named
    awesome-thing.rst.

    Please do not delete any of the sections in this template.  If you
    have nothing to say for a whole section, just write: None

    Note: This comment may be removed if desired, however the license notice
    above should remain.


==================
Multi-Region Trove
==================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::


Trove is currently able to deploy instances to multiple availability
zones within a region, but is limited to deployments within a single
Openstack region.  This specification outlines a proposal for allowing
Trove to deploy instances to multiple Openstack regions.

There are three different approaches to implementing multi-region
support in Trove.  The first approach would be for each region to have
it's own Trove controller and to implement a consistent view of Trove
instances across them; this would allow a user in any region to see
all trove instances within their region, regardless of which Trove
contoller created them.  The second approach would be to have a single
trove controller across all regions coordinated by a shared database
(such as Galera); this would allow users in any region to see all
trove instances in all regions.  The third approach would be to have
the Trove controller in each region to be independent, but able to
create instances in other regions; this would allow a user to see all
Trove instances created by the Trove controller in their region,
regardless of which region the instance is in, but they would not be
able to see Trove instances in their own region created by Trove
contollers in other regions.

This specification outlines a proposal that would allow the second and
third alternatives to be implemented.  It is the author's belief that
the first alternative would be far more complex, difficult to
implement, and error prone than the second and third options.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/multi-region


Problem Description
===================

Trove will be modified to be able to use Openstack's cross-region
client access to implement support for creating Trove instances in
other regions.  Essentially, one Trove controller will be able to
access Nova and Cinder services in multiple Openstack regions.

Multi-region support will require that the Keystone service be
federated between the regions, effectively allowing the Trove
controller to access services in multiple regions using a single,
common authentication.  This functionality is currently supported in
Openstack.

Object storage (such as Swift) may be federated between the regions,
or each region may have an independent object storage service.  Where
regions represent physically distinct data centres, a single shared
implementation of object storage may be preferrable as it would allow
data to be shared efficiently between the regions, rather than being
transferred in it's entirety upon each access.

In the default configuration, each region will host an independent set
of Trove contoller services, with each region having it's own Trove
API, Taskmanager, and Conductor services backed by a separate Trove
database for each region.  When a Taskmanager in one region needs to
allocate resources (compute and block storage) in a different region,
it will use the OS_REGION_NAME parameter to the Nova and Cinder
clients to access the appropriate Openstack services in the other
region.  The Trove instances allocated in the second region will only
be visible to trove cli commands executed in the first region.

A second configuration will be possible where each region will host a
set of Trove services which share a common Trove database implemented
via a federated database product such as Galera clustering.  This will
allow users in each region to see all Trove instances, regardless of
in which region they are hosted, but may expose the Trove services to
the usual issues associated with running Openstack services on a
database which uses optimistic locking.  No testing of this
alternative is envisioned for the initial implementation of
multi-region support.

Implementing multi-region support as described in this document will
require that the instances in each region be on a network shared
across all regions, and that the instances be able to access the
Rabbit network in each region.


Proposed Change
===============

Supporting multiple regions, as laid out in this document, will
primary consist of allowing the Trove services (API, Taskmanager, and
Guestagent) to provide an OS_REGION_NAME parameter when accessing the
clients for Nova and Cinder.  Adding this support will encompass the
following components:

* Add 'region' field to the Instances table in the Trove database.
* Enhance the CLI and REST API to allow 'region name' to be specified
  for each instance to be created (both single instance and clusters)
* Add 'region name' to guest agent RPC calls as needed (backup_info
  parameter of prepare call)
* Enhance each datastore to use the 'region name' as appropriate

When specifying that an instance be started in a different region,
Trove will need to ensure that an appropriate image is available in
the target region.  To do so, trove will contact the Glance service in
the other region to retrieve the metadata for the image of the same
name as specified in the datastore (in the first region).  The
checksums of the images in both regions will be compared to ensure
that the same image in installed in each region.


Configuration
-------------

No changes to configuration files are envisioned.

Database
--------

A 'region_name' field will be added to the Trove 'instances' table.

Migration scripts will be provided to add 'region_name' parameters to
the above listed tables during Openstack release upgrades.

A  region_name property  will be  added  to the  DBInstance class  and
shadowed in the SimpleInstance class.

Public API
----------

A "region" parameter will be added to the following REST APIs to
indicate the region in which the specified resource should be created.
If the "region" parameter is not specified, the resource will be
created in the region in which the command is executed.

Operations which do not create new resources, such as the list and
show APIs, do not require additional region parameters.  For those
APIs, the region would be specified via the --os-region-name
parameter.

When the Taskmanager is requested to create an instance in a region
different than its own, it will need to ensure that a suitable image
is available in that region to create the instance (as it will not be
possible to tell the Nova in RegionB to use an image from RegionA).
To create an instance in RegionB, the Taskmanager in RegionA will
proceed as follows:

#. Retrieve the name of the appropriate image from the appropriate
   datastore_version in RegionA
#. Retrieve the checksum from Glance for the image in RegionA
#. Ensure that trove in RegionB has a datastore_version of the same
   name, and that datastore_version specifies an image of the same
   name
#. Retrieve the checksum of the image from the Glance in RegionB
#. Ensure that the image in both regions have identical checksums
#. Follow a procedure similar to that above to ensure that a similarly
   named flavour exists in both regions and has similar properties
#. Ask Nova in RegionB to create an instance with the appropriate
   image name and flavour


Instance Create
///////////////

Request::

    POST v1/<tenant_id>/instances
    {
        "instance": {
            "volume": {
                "type": null,
                "size": 1
            },
            "flavorRef": 11,
            "name": "m",
            "replica_count": 1,
            "replica_of": "0d5e5bcc-5c60-4703-b4b3-17f32e0abe72",
            "region": "RegionA"
        }
    }

Response::

    {
        "instance": {
            "created": "2016-03-08T16:13:30",
            "datastore": {
                "type": "mysql",
                "version": "5.6"
            },
            "flavor": {
                "id": "11",
                "links": [
                    {
                        "href": "https://<ip>:8779/v1.0/adbe7218e9f54369a0898f36d9c7a66d/flavors/11",
                        "rel": "self"
                    },
                    {
                        "href": "https://<ip>:8779/flavors/11",
                        "rel": "bookmark"
                    }
                ]
            },
            "id": "0d5e5bcc-5c60-4703-b4b3-17f32e0abe64",
            "links": [
                {
                    "href": "https://<ip>:8779/v1.0/adbe7218e9f54369a0898f36d9c7a66d/instances/0d5e5bcc-5c60-4703-b4b3-17f32e0abe64",
                    "rel": "self"
                },
                {
                    "href": "https://<ip>:8779/instances/0d5e5bcc-5c60-4703-b4b3-17f32e0abe64",
                    "rel": "bookmark"
                }
            ],
            "name": "m",
            "status": "BUILD",
            "updated": "2016-03-08T16:13:30",
            "volume": {
                "size": 1
            },
            "region": "RegionA"
        }
    }

Cluster Create
//////////////

Request::

    POST /v1.0/<tenant_id>/clusters
    {
      "cluster": {
        "name": "products",
        "datastore": {
          "type": "percona",
          "version": "5.5"
        },
        "instances": [
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
            "region": "RegionA",
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
            "region": "RegionA",
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
            "region": "RegionB",
          }
        ],
      }
    }

Response::

    {
      "cluster": {
        "id": "dfbbd9ca-b5e1-4028-adb7-f78643e17998",
        "task": {
          "id": 2,
          "name": "BUILDING",
          "description": "Building the initial cluster."
        },
        "name": "products",
        "created": "2014-04-25T20:19:23",
        "updated": "2014-04-25T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "percona",
          "version": "5.5"
        },
        "region": "RegionA",
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "status": "BUILD",
            "flavor": {
              "id": "2",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "region": "RegionA",
          },
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
            "status": "BUILD",
            "flavor": {
              "id": "2",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "region": "RegionA",
          },
          {
            "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
            "status": "BUILD",
            "flavor": {
              "id": "2",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "region": "RegionB",
          }
        ],
      }
    }


cluster-grow
////////////

Request::

    POST /v1.0/<tenant_id>/clusters/<cluster-id>/action
    {
        "grow": [
          {
            "name": "redis-clstr-member-5",
            "instance_type": "master",
            "flavorRef": "2",
            "volume": {
              "size": 2
            },
          },
          {
            "name": "redis-clstr-member-6",
            "instance_type": "slave",
            "related_to": "redis-clstr-member-5",
            "flavorRef": "2",
            "volume": {
              "size": 2
            },
            "region": "RegionB",
          }
        ]
    }

Response::

    {
      "cluster": {
        "id": "edaac9ca-b5e1-4028-adb7-fa7653e11224",
        "task": {
          "id": 2,
          "name": "BUILDING",
          "description": "Building the initial cluster."
        },
        "name": "redis-clstr",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "redis",
          "version": "3.0"
        },
        "ip": [],
        "region": "RegionA",
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "redis-clstr-member-5",
            "instance_type": "master",
            "status": "BUILD",
            "ip": [],
            "links": [{...}],
            "flavor": {
              "id": "2",
              "links": [{...}]
            },
            "volume": {
              "size": 2
            }
            "region": "RegionA",
          },
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
            "name": "redis-clstr-member-6",
            "instance_type": "slave",
            "related_to": "redis-clstr-member-5",
            "status": "BUILD",
            "ip": [],
            "links": [{...}],
            "flavor": {
              "id": "2",
              "links": [{...}]
            },
            "volume": {
              "size": 2
            }
            "region": "RegionB",
          },
        ]
      }
    }


Public API Security
-------------------

This change should not have security impact.

Python API
----------

"region" parameters will be added to the Instances.create(),
Clusters.create(), and Clusters.grow() calls.

CLI (python-troveclient)
------------------------

A "--region" option will be added to the "trove create" CLI command
corresponding to the "region" parameter in the Instances.create() Python API.

A "region" option will be added to the "--instance" option of the
"trove cluster-create" and "trove cluster-grow" CLI commands
corresponding to the Clusters.create() and Clusters.grow() Python
APIs.

Internal API
------------

The "region" parameter will be added to the appropriate Taskmanager
calls to support instance creation for both single instance and
cluster creation.

The Trove Instance class already has a nova_client property that
creates a unique client connection for each guest instance.  That call
will be enhanced to specify the name of the region in which the
instance exists; the create_nova_client() method in remote.py will be
enhanced to optionally take a region name parameter.


Guest Agent
-----------

The only change to the guest agent should be to support initializing a
database with data stored in a different region.  This would occur
during the prepare process, and is to support creating a replica from
a backup of a master in a differnt region.

The guest.prepare() call already takes a structure called backup_info
which contains details of the backup to be used to initialize the
database.  This change will add a member "region" to the backup_info
structure which will be the name of the region containing the backup.
That region name will be passed to the Swift client to tell Swift in
which region the backup was created; note, however, that it is
expected that Swift will normally be configured to be shared across
regions and so be able to optimize object access from all regions.

When a taskmanager in RegionA creates an instance in RegionB, it will
pass a guestagent.conf to the new instance.  The new instance in
RegionB will use the rabbit configuration parameters in the conf file
to determine how to connect to the rabbit broker in RegionA.  No
changes should be required to the existing guest agent to support this
functionality.


Alternatives
------------

As indicated in the introduction, an alternative to the design
suggested here would be to have the trove controllers perform their
own synchronization giving each controller a view of every Trove
instance.  This would require that all operations be coordinated with
the Trove controllers in every region, either via some form of Two
Phase Commit or some Eventual Consistency mechanism.  Implementing
this would be quite complex and offer little benefit beyond the shared
database implementation.



Dashboard Impact (UX)
=====================

The user should be able to select the region in which a new instance
or cluster is to be created.

Panels which display properties of instances or clusters should be
enhanced to display the region name.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  6-morgan

Milestones
----------

Target Milestone for completion:
  eg. Liberty-1

Work Items
----------

Already implemented, code awaiting spec approval.


Upgrade Implications
====================

No upgrade implications are envisioned as a result of this change.


Dependencies
============

No dependecies.


Testing
=======

No int-tests will be developed for this feature due to the difficulty
of creating multiple regions within devstack.


Documentation Impact
====================

Documentation will be necessary for the new parameters to the Trove
CLI commands.


References
==========


Appendix
========

None.
