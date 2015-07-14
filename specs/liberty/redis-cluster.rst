..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

 Sections of this template were taken directly from the Nova spec
 template at:
 https://github.com/openstack/nova-specs/blob/master/specs/template.rst
..

=======================
Redis Clustering
=======================

https://blueprints.launchpad.net/trove/+spec/redis-cluster

Redis is a NoSQL database designed for high performance caching and
persistence of key/value data.  This document outlines a proposal for
implementing clustering for Redis.

Problem Description
===================

Implement clustering for Redis.

Proposed Change
===============

The Redis clustering feature will strive to implement the minimum
functionality required for a user to implement a Redis cluster in a
Trove environment.  While Trove will provide functionality to support
operations not possible directly through the Redis API, functionality
will be left to the user to perform via the Redis API wherever
possible.  This decision is based on the belief that it would be
extremely difficult to provide all the required functionality through
a web interface, and that Redis users will be familiar with the Redis
command set.

Configuration
-------------

The following configuration values will be implemented in the Redis
configuration group::

    cfg.BoolOpt('cluster_support', default=True,
                help='Enable clusters to be created and managed.'),
    cfg.StrOpt('api_strategy',
               default='trove.common.strategies.cluster.experimental.'
               'redis.api.RedisAPIStrategy',
               help='Class that implements datastore-specific API logic.'),
    cfg.StrOpt('taskmanager_strategy',
               default='trove.common.strategies.cluster.experimental.redis.'
               'taskmanager.RedisTaskManagerStrategy',
               help='Class that implements datastore-specific task manager '
                    'logic.'),
    cfg.StrOpt('guestagent_strategy',
               default='trove.common.strategies.cluster.experimental.'
               'redis.guestagent.RedisGuestAgentStrategy',
               help='Class that implements datastore-specific Guest Agent API '
                    'logic.'),


Database
--------

No changes.

REST API
----------

--------------
Create Cluster
--------------

The cluster-create command will allow the user to create a cluster
with the specified number of master nodes.  The data slots will be
evenly divided between the created nodes.

Request::

    POST /v1.0/<tenant_id>/clusters
    {
      "cluster": {
        "name": "redis-clstr",
        "datastore": {
          "type": "redis",
          "version": "3.0"
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
          },
          {
            "flavorRef": "2",
            "volume": {
              "size": 2
            }
          },
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
        "name": "redis-clstr",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "redis",
          "version": "3.0"
        },
        "ip": [],
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "redis-clstr-member-1",
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
            "name": "redis-clstr-member-2",
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
            "name": "redis-clstr-member-3",
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
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "redis-clstr-member-4",
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
        ]
      }
    }


HTTP Codes::

    202 - Accepted.
    400 - BadRequest. Server could not understand request.
    403 - Forbidden. Local storage not specified in flavor ID: <ID>.
    403 - Forbidden. A flavor is required for each instance in the cluster.
    404 - Not Found. Flavor not found.

------------
Grow Cluster
------------

Adds nodes to a cluster.  The added nodes will be master nodes empty
of data and will have no slots assigned to them.

Request::

    POST /v1.0/<tenant_id>/clusters/edaac9ca-b5e1-4028-adb7-fa7653e11224/action
    {
        "grow": [
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
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "redis-clstr-member-5",
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
            "name": "redis-clstr-member-6",
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
        ]
      }
    }


HTTP Codes::

    202 - Accepted.
    400 - BadRequest. Server could not understand request.
    403 - Forbidden. Local storage not specified in flavor ID: <ID>.
    403 - Forbidden. A flavor is required for each instance in the cluster.
    404 - Not Found. Flavor not found.


--------------
Shrink Cluster
--------------

Removes the specified nodes from the cluster.  It is expected that all
data slots have been removed from the node - the shrink operation will
fail otherwise.

Request::

    POST /v1.0/<tenant_id>/clusters/<cluster_id>/action
        "shrink": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
          },
          {
            "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
          }
        ]
    }

Response::

    N/A

HTTP codes::

    202 - Accepted.
    403 - Forbidden.  One or more nodes have data slots assigned.
    404 - Not found.  Instance <id> does not exist.

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
        "name": "redis-clstr",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "redis",
          "version": "3.0"
        },
        "ip": ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4",],
        "instances": [
          {
            "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
            "name": "redis-clstr-member-1",
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
            "name": "redis-clstr-member-2",
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
            "name": "redis-clstr-member-3",
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
          },
          {
            "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
            "name": "redis-clstr-member-4",
            "status": "BUILD",
            "ip": ["10.0.0.4"],
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
        "name": "redis-clstr-member-1",
        "created": "2015-01-29T20:19:23",
        "updated": "2015-01-29T20:19:23",
        "links": [{...}],
        "datastore": {
          "type": "redis",
          "version": "3.0"
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
          "name": "redis-clstr",
          "created": "2015-01-29T20:19:23",
          "updated": "2015-01-29T20:19:23",
          "links": [{...}],
          "datastore": {
            "type": "redis",
            "version": "3.0"
          },
          "instances": [
            {
              "id": "416b0b16-ba55-4302-bbd3-ff566032e1c1",
              "name": "redis-clstr-member-1",
              "links": [{...}],
            }
            {
              "id": "965ef811-7c1d-47fc-89f2-a89dfdd23ef2",
              "name": "redis-clstr-member-2",
              "links": [{...}],
            },
            {
              "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
              "name": "redis-clstr-member-3",
              "links": [{...}],
            },
            {
              "id": "3642f41c-e8ad-4164-a089-3891bf7f2d2b",
              "name": "redis-clstr-member-4",
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

Request::

    DELETE /v1.0/<tenant_id>/clusters/<cluster_id>

Response::

    N/A

HTTP codes::

    202 - Accepted.
    404 - Not found

Public API
----------

No public API changes.

Public API Security
-------------------

n/a

Python API
----------

No Python API changes.

CLI (python-troveclient)
------------------------

No CLI changes.

Internal API
------------

No changes are envisioned to the guestagent api, beyond implementing
the existing API methods.

Guest Agent
-----------

The following methods will be implemented in the RedisGuestAgentAPI::

    def get_node_ip(self):
        LOG.debug("Retrieve ip info from node.")
        return self._call("get_node_ip",
                          guest_api.AGENT_HIGH_TIMEOUT, self.version_cap)

    def get_node_id_for_removal(self):
        LOG.debug("Validating cluster node removal.")
        return self._call("get_node_id_for_removal",
                          guest_api.AGENT_HIGH_TIMEOUT, self.version_cap)

    def remove_nodes(self, node_ids):
        LOG.debug("Removing nodes from cluster.")
        return self._call("remove_nodes", guest_api.AGENT_HIGH_TIMEOUT,
                          self.version_cap, node_ids=node_ids)

    def cluster_meet(self, ip, port):
        LOG.debug("Joining node to cluster.")
        return self._call("cluster_meet", guest_api.AGENT_HIGH_TIMEOUT,
                          self.version_cap, ip=ip, port=port)

    def cluster_addslots(self, first_slot, last_slot):
        LOG.debug("Adding slots %s-%s to cluster.", first_slot, last_slot)
        return self._call("cluster_addslots",
                          guest_api.AGENT_HIGH_TIMEOUT, self.version_cap,
                          first_slot=first_slot, last_slot=last_slot)

    def cluster_complete(self):
        LOG.debug("Notifying cluster install completion.")
        return self._call("cluster_complete", guest_api.AGENT_HIGH_TIMEOUT,
                          self.version_cap)

Alternatives
------------

n/a

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  vgnbkr

Milestones
----------

Target Milestone for completion:
  Liberty-3

Work Items
----------

- implement clustering for Redis

implement new Taskmanager cluster strategy for Redis
implement python API and shell for shrink/grow (this may be already done
through cluster-scaling bp implementation)
add grow/shrink to cluster strategy (in absence of scaling implementation)
implement guest agent support for joining/leaving a cluster
implement unit tests as appropriate
implement int-test if the mechanism for doing so has been worked out by
that time


Upgrade Implications
====================

As this is a new implementation, no upgrade implications are
envisioned.


Dependencies
============

- This functionality depends on the cluster scaling functionality
  outlined in
  https://blueprints.launchpad.net/trove/+spec/cluster-scaling


Testing
=======

- Implementation of int-tests for clustering is still being worked out
  for MongoDB and Cassandra.  It is expected that Redis will
  implement/run similar int-tests.

Documentation Impact
====================

- Datastore documentation for Redis will need to be updated to reflect
  clustering support.


References
==========

http://redis.io/topics/cluster-tutorial
http://redis.io/topics/cluster-spec
