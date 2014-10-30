..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

======================================
Implement Percona cluster provisioning
======================================

To continue the Trove HA story, high availability of database instances is
required in order to give users a peace of mind when running their production
workloads in Trove. Apart from replication, clustering makes the deployment
to be highly available by allowing data to be accessed from any node in the
cluster. It enhances system uptime, it prevents from data loss and makes the
architecture more scalable for future growth. Trove Clustering for the
Percona datastore will be based on the Percona XtraDB Cluster, which is a
true Multimaster Cluster based on synchronous replication.

This change will focus on the Create, List, Show, and Delete of a Peronca
cluster. Grow and shrink of the cluster will be handled in a separate
blueprint.

https://blueprints.launchpad.net/trove/+spec/support-pxc-56

Problem Description
===================

The Percona datastore does not have support for clustering. Adding a cluster
implementation will allow users to create read and write scalable and highly
available deployments.


Proposed Change
===============

Percona cluster will leverage the base cluster implementation that currently
exists in Trove by creating plugabble and configurable strategies.

Requirements:

- The cluster should not have less than three nodes.
- Initial cluster creation will start with 3 or more.
- The cluster will return all IPs of its nodes.
  This is done so that the cluster can be used for multi write and read.
- The name of each instance will be automatically generated;
  it will be the <cluster_name>-<instance_num>.
- The clusters shall have nodes of same volumes but not for flavors.
- Clusters shall allow the instances/cluster members to be resizable for
  volume and flavors. No validation will occur if a user resizes volumes
  or flavors of an instance.

The following will be changed:

- A percona-cluster implementation will be added to
  common/strategies/cluster/experimental/mysql/xtradbcluster
- Task manager strategy to handle the cluster provisioning for percona.
- Guestagent strategy to handle the clustering provisioning,
  configuration and execution.
- Unit and integration tests.


Configuration
-------------

A new datastore configuration section will be added.  This initial
implementation will add no Percona-Cluster specific configuration
options.

Trove Integration
-----------------

The Redstack script will create a datastore configuration for
percona-cluster to open ports 3306, 4444, 4567, and 4568.

Elements will be added to support "redstack kick-start
percona-cluster-5.6".


Database
--------

This implementation will leverage the existing database schema for cluster.

Public API
----------

The API request for creating/deleting cluster will remain unchanged. However,
there will be subtle differences in the response. Percona clustering will
return all IPs of its nodes. This will be used for the user who wants to scale
read/write.

--------------
Create Cluster
--------------

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

--------------
Show Cluster
--------------

Request::

    GET /v1.0/<tenant_id>/clusters/dfbbd9ca-b5e1-4028-adb7-f78643e17998

Response::

    {
      "cluster": {
        "id": "dfbbd9ca-b5e1-4028-adb7-f78643e17998",
        "task": {
          "id": 1,
          "name": "NONE",
          "description": "No tasks for the cluster."
        },
        "name": "products",
        "created": "2014-04-25T20:19:23",
        "updated": "2014-04-25T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "percona",
          "version": "5.5"
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

    GET /v1.0/<tenant_id>/clusters/dfbbd9ca-b5e1-4028-adb7-f78643e17998/instances/416b0b16-ba55-4302-bbd3-ff566032e1c1

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
          "type": "percona",
          "version": "5.5"
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
          "id": "dfbbd9ca-b5e1-4028-adb7-f78643e17998",
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
            "type": "percona",
            "version": "5.5"
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

    DELETE /v1.0/<tenant_id>/clusters/dfbbd9ca-b5e1-4028-adb7-f78643e17998

Response::

    HTTP 202 (Empty Body)


Public API Security
-------------------

None

Internal API
------------

No changes in the internal API yet.

Guest Agent
-----------

No API changes in the guest agent. This feature will just be adding a new
strategy to support a different type of clustering.


CLI (python-troveclient)
------------------------

The following illustrates the clustering CLI

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

      --instance <flavor_id=flavor_id,volume=volume,parameters=<key=value>>
                            Create an instance for the cluster. Specify
                            multiple times to create multiple instances.

Request::

    $ trove cluster-create products percona "5.5" \
      --instance flavor_id=7,volume=2 \
      --instance flavor_id=7,volume=2 \
      --instance flavor_id=7,volume=2

Response::

    +-------------------+--------------------------------------+
    | Property          | Value                                |
    +-------------------+--------------------------------------+
    | created           | 2014-08-16T01:46:51                  |
    | datastore         | percona                              |
    | datastore_version | 5.5                                  |
    | id                | aa6ef0f5-dbef-48cd-8952-573ad881e717 |
    | name              | products                             |
    | task_description  | Building the initial cluster.        |
    | task_name         | BUILDING                             |
    | updated           | 2014-08-16T01:46:51                  |
    +-------------------+--------------------------------------+

The cluster-create command will create a cluster of functionally
equivalent trove instances.  Trove will choose a instance to start with
the --wsrep-new-cluster option, then the remaining instances will be
started sequentially.  The cluster will be marked ACTIVE when all
instances have started and the database is available for use.


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
    | created           | 2014-08-16T01:46:51                  |
    | datastore         | percona                              |
    | datastore_version | 5.5                                  |
    | id                | aa6ef0f5-dbef-48cd-8952-573ad881e717 |
    | ip                | 10.0.0.2, 10.0.0.1, 10.0.0.3         |
    | name              | products                             |
    | task_description  | No tasks for the cluster.            |
    | task_name         | NONE                                 |
    | updated           | 2014-08-16T01:59:33                  |
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
    | uuid-1 | products | percona   | 5.5       | ip1      | NONE      |
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

Replication Impact
------------------

Due to the scope of adding a replica to a cluster this will be disabled
as part of this blueprint and added as a separate blueprint. [4]_


Python API
----------

???


Alternatives
------------

None defined yet.


Upgrade Implications
====================

To enable MySQL cluster support, a different package will be needed to install
on the guest instance rather than the default. There are 2 ways to mitigate
this in an upgrade path.

1. Update the packages installed on the datastore version.

2. Build a new image with the new package installed into the guest image.


Implementation
==============

Assignee(s)
-----------

+---------------+--------------+---------+--------------------+
+ Name          + Launchpad Id + IRC     + Email              +
+===============+==============+=========+====================+
+ Steve Leon    + steve-leon   + esmute  + kokhang@gmail.com  +
+---------------+--------------+---------+--------------------+
+ Morgan Jones  + 6-morgan     + vgnbkr  + morgan@tesora.com  +
+---------------+--------------+---------+--------------------+
+ Craig Vyvial  + cp16net      + cp16net + cp16net@gmail.com  +
+---------------+--------------+---------+--------------------+


Milestones
----------

Liberty-3


Work Items
----------

- trove-integration change to add percona-xtradb-cluster-server package
- API strategy implementation
- Taskmanager strategy implementation
- Guestagent strategy implementation
- Unit and integration tests


Dependencies
============

None

Testing
=======

There will be unit tests that test every components in the strategies.
There will be integration tests which will test end-to-end cluster features


Documentation Impact
====================

The response API will look different due to the nature of XtraDB clusters.
For example, the view will contain all the IPs of the instances.


References
==========

API strategy to handle clustering request for Percona. Besides the existing
API, there will be new API to grow/shrink cluster handled in another
blueprint. (bp/cluster-scaling [1]_ )

Trove does not monitor the status of cluster instances.  Should an instance
in the cluster become detached from the primary instance it will be up to
the user to detect the situation and take corrective action. If the instance
does not re-attach to the cluster in a state where an Incremental State
Transfer (IST) is possible, it is suggested to delete the
instance and add a new node to the cluster. (In the future, a user will be
able to delete the instance from a cluster via the shrink action and add
a new instance to the cluster with the grow action.)

In the event of a nova compute reboot, the nodes will automatically
restart, and the cluster will automatically recover provided that the
nodes can determine that the PRIMARY component can be properly
recovered.  In the case that the PRIMARY component cannot be
recovered, operator intervention would be required to manually restart
the cluster.



List of other cluster related blueprints. These blueprints will likely cause
conflicts with changes.

.. [1] bp/cluster-scaling: https://blueprints.launchpad.net/trove/+spec/cluster-scaling
.. [2] bp/mysql-manager-refactor: https://blueprints.launchpad.net/trove/+spec/mysql-manager-refactor
.. [3] bp/cluster-user-management: https://blueprints.launchpad.net/trove/+spec/cluster-user-management
.. [4] percona-xtradb-with-replica: https://blueprints.launchpad.net/trove/+spec/percona-add-replica-of-cluster
