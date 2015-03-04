..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

========================================
Implement Vertica cluster provisioning
========================================

https://blueprints.launchpad.net/trove/+spec/implement-vertica-cluster


Problem description
===================

Provide HP Vertica CE clusters through the Trove Clustering API.

Proposed change
===============

Trove provides a well-designed framework for implementing clustering
for different datastores.
The Vertica datastore requires additional effort to accomplish clustering.

HP Vertica CE requires a minimum of 3 nodes to achieve fault tolerance.

Development plan:

    - API strategy, needed for handling clustering requests for Vertica.
    - Taskmanager strategy, needed to handle cluster provisioning for Vertica.
    - Guestagent strategy, needed to handle RPC API calls from
      Taskmanager to guest instances.
    - Unit and integration tests.
    - The cluster will return IPs of its nodes. This is done so that the
      cluster can be used for multi write and read.
    - The name of each instance will be automatically generated;
      it will be the <cluster_name>-member-<instance_num>.
    - There will be no grow/shrink functions to the cluster,
      since the CE edition provides for a maximum of 3-nodes and
      a 2-node HP Vertica Cluster is not fault-tolerable.

How to deploy HP Vertica Cluster
--------------------------------
    To bind multiple instances into a Vertica cluster, run the command "install_vertica" with each node IP.
    Next, run admintools to create a database on all included nodes in the cluster.

    Step-by-Step guide for cluster provisioning:

    - Spin up N instances.
    - Once N instances are up and running, collect their IPs.
    - Enable password-less ssh between member instances for root and dbadmin users, by copying public key to authorized_keys.
    - Classify one of the nodes as first node(first-node is only logical to trove, Vertica has no preference as such.)
    - From first node, run install_vertica with all IPs from this node to stich all nodes into vertica cluster.
    - From first node, run admintools to create a database including all nodes in the cluster.


Configuration
-------------

Vertica datastore needs new configuration options to enable clustering:

  cluster_support - describes the availability of clustering feature.
     Type: Boolean

  api_strategy - fully qualified class name of API strategy implementation.
     Type: String

  taskmanager_strategy - fully qualified class name of a Taskmanager implementation.
     Type: String

  guestagent_strategy - fully qualified class name of a Guestagent implementation.
     Type: String


Database
--------

This implementation will leverage the existing database schema for cluster.

Public API
----------

The API request for creating/deleting cluster will remain unchanged.
However, there will be subtle differences in the response.
Vertica clustering will return IPs of all of its nodes.
This will be used for user who want to scale read/write.

--------------
Create Cluster
--------------

Request::

    POST /v1.0/<tenant_id>/clusters
    {
      "cluster": {
        "name": "vertica-clstr",
        "datastore": {
          "type": "vertica",
          "version": "7.1"
        },
        "instances": [
          {
            "flavorRef": "2",
            "volume": {
              "size": 2
            }
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 2
            }
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 2
            }
          }
        ]
      }
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
        "name": "vertica-clstr",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "vertica",
          "version": "7.1"
        },
        "ip": [],
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "vertica-clstr-member-1",
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
          },
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
            "name": "vertica-clstr-member-2",
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
          },
          {
            "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
            "name": "vertica-clstr-member-3",
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
          }
        ]
      }
    }


HTTP Codes::

    202 - Accepted.
    400 - BadRequest. Local storage not specified in flavor ID: <ID>.
    400 - BadRequest. The number of instances for your cluster must be 3.
    400 - BadRequest. A volume size is required for each instance in the cluster.
    400 - BadRequest. A flavor is required for each instance in the cluster.
    404 - Not Found. Flavor not found.


--------------
Show Cluster
--------------

Request::

    GET /v1.0/<tenant_id>/clusters/edaac9ca-b5e1-4028-adb7-fa7653e11224

Response::

    {
      "cluster": {
        "id": "edaac9ca-b5e1-4028-adb7-fa7653e11224",
        "task": {
          "id": 1,
          "name": "NONE",
          "description": "No tasks for the cluster."
        },
        "name": "vertica-clstr",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "vertica",
          "version": "7.1"
        },
        "ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3",],
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "vertica-clstr-member-1",
            "status": "ACTIVE",
            "ip": ["10.0.0.1"],
            "links": [{...}],
            "flavor": {
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 2
            },
          }
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
            "name": "vertica-clstr-member-2",
            "status": "ACTIVE",
            "links": [{...}],
            "flavor": {
            "ip": ["10.0.0.2"],
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 2
            },
          },
          {
            "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
            "name": "vertica-clstr-member-3",
            "status": "BUILD",
            "ip": ["10.0.0.3"],
            "links": [{...}],
            "flavor": {
              "id": "7",
              "links": [{...}]
            },
            "volume": {
              "size": 2
            },
          }
        ]
      }
    }



HTTP Codes::

    200 - OK.
    404 - Not Found. Cluster not found.


-------------
Show Instance
-------------

Request::

    GET /v1.0/<tenant_id>/clusters/edaac9ca-b5e1-4028-adb7-fa7653e11224/instances/416b0b16-ba55-4302-bbd3-ff566032e1c1

Response::

    {
      "instance": {
        "status": "ACTIVE",
        "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
        "cluster_id": "edaac9ca-b5e1-4028-adb7-fa7653e11224",
        "name": "vertica-clstr-member-1",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "vertica",
          "version": "7.1"
        },
        "ip": ["10.0.0.1"],
        "flavor": {
          "id": "7",
          "links": [{...}],
        },
        "volume": {
          "size": 2,
          "used": 0.17
        }
      }
    }


HTTP Codes::

    200 - OK.
    404 - Not Found. Cluster not found.
    404 - Not Found. Instance not found.


-------------
List Clusters
-------------

Request::

    GET /v1.0/<tenant_id>/clusters

Response::

    {
      "clusters": [
        {
          "id": "edaac9ca-b5e1-4028-adb7-fa7653e11224",
          "task": {
            "id": 1,
            "name": "NONE",
            "description": "No tasks for the cluster."
          },
          "name": "vertica-clstr",
          "created": "2015-01-29T20:19:23",
          "updated": "2015-01-29T20:19:23",
          "links": [{...}],
          "datastore": {
            "type": "vertica",
            "version": "7.1"
          },
          "instances": [
            {
              "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
              "name": "vertica-clstr-member-1",
              "links": [{...}],
            }
            {
              "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
              "name": "vertica-clstr-member-2",
              "links": [{...}],
            },
            {
              "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
              "name": "vertica-clstr-member-3",
              "links": [{...}],
            }
          ]
        },
        ...
      ]
    }


HTTP Codes::

    200 - OK.


--------------
Delete Cluster
--------------


HTTP Method::

    DELETE

Route::

    /v1.0/<tenant_id>/clusters/<cluster_id>

Request::

    {

    }

Response::

    {

    }

HTTP codes::

    202 - Accepted.


---------------
Cluster Actions
---------------

No cluster actions.

Internal API
------------

From API service to Taskmanager service:

 - create_cluster:

    - checks if all instances are in BUILDING state.
    - designates one of the instances as first instance.
    - calls guest "get_keys" to receive public key from all member instances.
    - calls guest "authorize_keys" to register set of public keys to all member instances.
    - calls guest "install_cluster" to bind all nodes into a cluster with a database.
    - calls guest "cluster_complete" to all nodes to complete the activity.
    - checks if all instances are in ACTIVE state.

Guest Agent
-----------

To accomplish clustering for Vertica datastore more RPC APIs would be needed
as per new guestagent-strategy.


Implementation
==============

Assignee(s)
-----------

Primary assignee:

- sushil.kumar3@hp.com (Primary Assignee)
- saurabh.surana@hp.com
- jonathan.halterman@hp.com

Milestones
----------
"Kilo-3"


Work Items
----------

- Implement API strategy.
- Implement Taskmanager strategy.
- Implement Guestagent strategy.
- Unit and integration tests


Dependencies
============

Single instance Vertica datastore to be merged first into Trove.


Testing
=======

There will be unit tests that test every components in the strategies.
There will be integration tests which will test cluster features.


Documentation Impact
====================

The docs would need updates for:

    - Trove Capabilities for Vertica Clusters.
    - Vertica cluster creation methodolgy.
    - Modified responses of existing due to nature of HP Vertica clustering.


References
==========

[1] http://my.vertica.com/docs/7.1.x/HTML/index.htm
