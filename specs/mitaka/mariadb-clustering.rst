..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/juno-template.rst

=====================================
Implement Galera cluster provisioning
=====================================

.. If section numbers are desired, unindent this
    .. sectnum::

.. If a TOC is desired, unindent this
    .. contents::

High availability of database instances is required in order to build users
confidence when running production workloads in Trove.
Apart from replication, clustering ensures the deployment is highly available
by allowing data to be accessed from any node in the cluster.
It enhances system uptime, prevents from data loss and makes the architecture
more scalable for future growth.
Currently Trove has support for MongoDB clusters and Percona clusters.
Trove clustering for the MariaDB datastore will be based on Galera Cluster,
a synchronous multi-master database cluster.


Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/mariadb-clustering

Problem Description
===================

MariaDB datastore does not have support for clustering. Adding a cluster
implementation will allow users to create, read and write scalable and highly
available deployments.

Proposed Change
===============

Galera Cluster will leverage the base cluster implementation that currently
exists in Trove by creating pluggable and configurable strategies.

Requirements:

* An instance of Galera Cluster consists of a series of nodes,
  preferably three or more.
* Initial cluster creation will start with 3 or more nodes.
* The cluster inspection will return IPs of all its nodes in order to
  allow read and write to any node at any time.
* The name of each instance will be automatically generated.
* Clusters shall allow the cluster nodes to be resizable for volume
  and flavors.
  No validation will occur if a user resizes volumes or flavors
  of an instance.

The following will be changed:

* Base classes for Percona Cluster and Galera Cluster will be added to
  common/strategies/cluster/experimental/galera_common/{api,taskmanager,guestagent}.py
* Percona Cluster specialization will live under
  common/strategies/cluster/experimental/pxc/{api,taskmanger,guestagent}.py
  This contains the API, the taskmanager strategy to handle the
  cluster provisioning for Percona and the guestagent strategy
  to handle the cluster provisioning, configuration and execution.
* Galera Cluster specialization will be added to
  common/strategies/cluster/experimental/mariadb/{api,taskmanager,guestagent}.py
  This contains the API, the taskmanager strategy to handle the
  cluster provisioning for Galera and the guestagent strategy
  to handle the cluster provisioning, configuration and execution.
* Unit and integration tests

Configuration
-------------

A new datastore configuration section will be added.
This initial implementation will add no Galera Cluster
specific configuration options.

Database
--------

This implementation will leverage the existing database schema for cluster.

Public API
----------

The API request for creating/deleting cluster will remain unchanged.
However, there will be subtle differences in the response.
Galera clustering, as Percona implementation, will return all IPs of its nodes.
This will be used for the user who wants to scale read/write.

--------------
Create Cluster
--------------

Request::

    POST /v1.0/<tenant_id>/clusters
    {
      "cluster": {
        "name": "products",
        "datastore": {
          "type": "mariadb",
          "version": "10"
        },
        "instances": [
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 100
            },
          }
        ],
      }
    }

Response::

    {
      "cluster": {
        "id": "c33385b2-6c2a-491e-b44e-bcbb4af24136",
        "task": {
          "id": 2,
          "name": "BUILDING",
          "description": "Building the initial cluster."
        },
        "name": "products",
        "created": "2015-12-14T20:19:23",
        "updated": "2015-12-14T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "mariadb",
          "version": "10"
        },
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
          }
        ],
      }
    }

------------
Show Cluster
------------

Request::

    GET /v1.0/<tenant_id>/clusters/c33385b2-6c2a-491e-b44e-bcbb4af24136

Response::

    {
      "cluster": {
        "id": "c33385b2-6c2a-491e-b44e-bcbb4af24136",
        "task": {
          "id": 1,
          "name": "NONE",
          "description": "No tasks for the cluster."
        },
        "name": "products",
        "created": "2015-12-14T20:19:23",
        "updated": "2015-12-14T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "mariadb",
          "version": "10"
        },
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "status": "ACTIVE",
            "flavor": {
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "ip": "10.0.0.1"
          }
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
            "status": "ACTIVE",
            "flavor": {
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "ip": "10.0.0.2"
          },
          {
            "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
            "status": "BUILD",
            "flavor": {
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 100
            },
            "ip": "10.0.0.3"
          }
        ],
      }
    }

-------------
Show Instance
-------------

Request::

    GET /v1.0/<tenant_id>/clusters/c33385b2-6c2a-491e-b44e-bcbb4af24136/instances/416b0b16-ba55-4302-bbd3-ff566032e1c1

Response::

    {
      "instance": {
        "status": "ACTIVE",
        "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
        "cluster_id": "dfbbd9ca-b5e1-4028-adb7-f78643e17998",
        "name": "products-1",
        "created": "2014-04-25T20:19:23",
        "updated": "2014-04-25T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "mariadb",
          "version": "10"
        },
        "ip": ["10.0.0.1"],
        "flavor": {
          "id": "7",
          "links": [{...}],
        },
        "volume": {
          "size": 100,
          "used": 0.17
        },
      }
    }

-------------
List Clusters
-------------

Request::

    GET /v1.0/<tenant_id>/clusters

Response::

    {
      "clusters": [
        {
          "id": "c33385b2-6c2a-491e-b44e-bcbb4af24136",
          "task": {
            "id": 1,
            "name": "NONE",
            "description": "No tasks for the cluster."
          },
          "name": "products",
          "created": "2014-04-25T20:19:23",
          "updated": "2014-04-25T20:19:23",
          "links": [{...}],
          "ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3"],
          "datastore": {
            "type": "mariadb",
            "version": "10"
          },
          "instances": [
            {
              "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
              "status": "ACTIVE",
              "flavor": {
                "id": "7",
                "links": [{...}]
              },
              "volume": {
                "size": 100
              },
              "ip": "10.0.0.1",
            }
            {
              "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
              "status": "ACTIVE",
              "flavor": {
                "id": "7",
                "links": [{...}]
              },
              "volume": {
                "size": 100
              },
              "ip": "10.0.0.2",
            },
            {
              "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
              "status": "ACTIVE",
              "flavor": {
                "id": "7",
                "links": [{...}]
              },
              "volume": {
                "size": 100
              },
              "ip": "10.0.0.3",
            }
          ]
        },
        ...
      ]
    }

--------------
Delete Cluster
--------------

Request::

    DELETE /v1.0/<tenant_id>/clusters/c33385b2-6c2a-491e-b44e-bcbb4af24136

Response::

    HTTP 202 (Empty Body)

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

The same CLI implemented for Percona Cluster will be used to interact
with Galera Cluster. The main features are accessed as follows:

--------------
Create Cluster
--------------

::

    $ trove help cluster-create

    usage: trove cluster-create <name> <datastore> <datastore_version>
                                [--instance <instance>]

    Creates a new cluster.

    Positional arguments:
      <name>                Name of the cluster.
      <datastore>           A datastore name or UUID.
      <datastore_version>   A datastore version name or UUID.

    Optional arguments:

      --instance <flavor_id=flavor_id,volume=volume>
                            Create an instance for the cluster. Specify
                            multiple times to create multiple instances.

Request::

    $ trove cluster-create products mariadb "10" \
      --instance flavor_id=7,volume=2 \
      --instance flavor_id=7,volume=2 \
      --instance flavor_id=7,volume=2

Response::

    +-------------------+--------------------------------------+
    | Property          | Value                                |
    +-------------------+--------------------------------------+
    | created           | 2015-12-14T01:46:51                  |
    | datastore         | mariadb                              |
    | datastore_version | 10                                   |
    | id                | aa6ef0f5-dbef-48cd-8952-573ad881e717 |
    | name              | products                             |
    | task_description  | Building the initial cluster.        |
    | task_name         | BUILDING                             |
    | updated           | 2015-12-14T01:46:51                  |
    +-------------------+--------------------------------------+

The cluster-create command will create a cluster with identical instances.
Trove will choose a instance to start with the --wsrep-new-cluster option,
then the remaining instances will be started sequentially.
The cluster will be marked ACTIVE when all instances have started and
the database is available for use.


------------
Show Cluster
------------

::

    $ trove help cluster-show

    usage: trove cluster-show <cluster>

    Shows details of a cluster.

    Positional arguments:
      <cluster>  ID or name of the cluster.

Request::

    $ trove cluster-show aa6ef0f5-dbef-48cd-8952-573ad881e717

Response::

    +-------------------+--------------------------------------+
    | Property          | Value                                |
    +-------------------+--------------------------------------+
    | created           | 2015-12-14T01:46:51                  |
    | datastore         | mariadb                              |
    | datastore_version | 10                                   |
    | id                | aa6ef0f5-dbef-48cd-8952-573ad881e717 |
    | ip                | 10.0.0.2, 10.0.0.1, 10.0.0.3         |
    | name              | products                             |
    | task_description  | No tasks for the cluster.            |
    | task_name         | NONE                                 |
    | updated           | 2015-12-14T01:59:33                  |
    +-------------------+--------------------------------------+

---------------------
Show Cluster Instance
---------------------

::

    $ trove help cluster-instances

    usage: trove cluster-instances <cluster>

    Lists all instances of a cluster.

    Positional arguments:
      <cluster>  ID or name of the cluster.

Request::

    $ trove cluster-instances aa6ef0f5-dbef-48cd-8952-573ad881e717

Response::

    +-------------------------------------+----------------+-----------+------+
    | ID                                  | Name           | Flavor ID | Size |
    +-------------------------------------+----------------+-----------+------+
    | 45532fc4-661c-4030-8ca4-18f02a2b337 | products-1     | 7         |    2 |
    | 7458a98d-6f89-4dfd-bb61-5cf1d65c121 | products-2     | 8         |    2 |
    | 1557208f-5c23-4537-a9f2-52a9db38d3a | products-3     | 7         |    2 |
    +-------------------------------------+----------------+-----------+------+


-------------
List Clusters
-------------

::

    $ trove help cluster-list

    usage: trove cluster-list [--limit <limit>] [--marker <ID>]

    Lists all the clusters.

    Optional arguments:
      --limit <limit>  Limit the number of results displayed.
      --marker <ID>    Begin displaying the results for IDs greater than the
                       specified marker. When used with --limit, set this to
                       the last ID displayed in the previous run.

Request::

    $ trove cluster-list

Response::

    +--------+----------+-----------+-----------+----------+-----------+
    | ID     | Name     | Datastore | DsVersion | IP       | Task Name |
    +--------+----------+-----------+-----------+----------+-----------+
    | uuid-1 | products | mariadb   | 10        | ip1      | NONE      |
    | uuid-2 | items    | percona   | 5.5       | ip2, ip3 | BUILDING  |
    +--------+----------+-----------+-----------+----------+-----------+

--------------
Delete Cluster
--------------

::

    $ trove help cluster-delete

    usage: trove cluster-delete <cluster>

    Deletes a cluster.

    Positional arguments:
      <cluster>  ID of the cluster.

Request::

    $ trove cluster-delete aa6ef0f5-dbef-48cd-8952-573ad881e717

Response::

    (None)


Internal API
------------

None

Guest Agent
-----------

None

Alternatives
------------

None defined yet.


Dashboard Impact (UX)
=====================

The datastore must be enabled as a clustering datastore.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
    * vkmc
    * tellesnobrega

Milestones
----------

Target Milestone for completion:
    * Mitaka-3

Work Items
----------

* Trove Integration change to add support for mariadb-galera-server
* API strategy implementation
* Task Manager strategy implementation
* Guest Agent strategy implementation
* Unit and integration tests

Upgrade Implications
====================

To enable MariaDB cluster support, a different package needs to be installed
on the guest instance rather than the default. This can be solved by updating
the packages installed on the datastore version, although it is recommended
that a new image with the desired package is built and loaded.

Dependencies
============

None

Testing
=======

* Unit tests will be added to cover non-trivial code paths.
* Integration tests will be added to test end-to-end cluster features.

Documentation Impact
====================

The response API will look different due to the nature of Galera clusters.
Precisely, the view will contain all the IPs of the instances.

References
==========

Besides the existing API, there will be new API to grow/shrink cluster handled
in a follow up spec.

Trove does not monitor the status of the cluster instances. If an instance in
the cluster becames detached from the PRIMARY instance, it will responsability
of the user to detect the situation and take a corrective action.
If the instance does not re-attach to the cluster when a
Incremental State Transfer (IST) or State Snapshot Transfer (SST) is possible,
the user would need to delete the instance and add a new node to the cluster.
This will be later substituted by the grow/shrink cluster feature.

In the event of a Nova compute reboot, the nodes will automatically restart,
and the cluster will automatically recover provided that the nodes can
determine that the PRIMARY component can be properly recovered.
In the case that the PRIMARY component cannot be recovered,
operator intervention would be required to manually restart the cluster.

Appendix
========

None
