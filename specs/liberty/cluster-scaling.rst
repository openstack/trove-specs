..
    This work is licensed under a Creative Commons Attribution 3.0 Unported
    License.

    http://creativecommons.org/licenses/by/3.0/legalcode

    Sections of this template were taken directly from the Nova spec
    template at:
    https://github.com/openstack/nova-specs/blob/master/specs/template.rst

===============
Cluster Scaling
===============

Cluster support in trove currently has no direct support for growing
or shrinking clusters.  The current MongoDB cluster implementation
does currently support adding a "shard" via the "add-shard" action,
but it has been decided that this should be changed to use the new
cluster-grow functionality outlined in this spec.

The cluster-grow and cluster-shrink functionality has been discussed
at the previous mid-cycle and summit, and it was accepted as a
preferable alternative to the add-shard functionality currently
implemented by the MongoDB datastore.  This specification is intended
to develop a foundation for the shrink/grow functionality in Percona
and Redis clustering, and to be backward compatible with the MongoDB
clustering implementation.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/cluster-scaling


Problem Description
===================

Trove cluster support needs to be extended with support for increasing
or decreasing the size of a cluster.  This support will be provided by
adding new ReST APIs for cluster-grow and cluster-shrink with
corresponding CLI and python-troveclient support.

The MongoDB cluster implementation will be enhanced to support
cluster-grow in addition to the currently supported "add-shard"
action.


Proposed Change
===============

New ReST APIs
-------------

Two new ReST APIs will be added for this feature.

cluster-grow
////////////

Adds nodes to a cluster.

This new API adds 3 new attributes to the usual instance payload:

:name: Name to assign to the instance

:instance_type: Datastore specific type of the instance (eg.,
                query/replica for Mongo, master/slave for Redis).

:related_to: Defines a relationship from one member to another.  The
             value is datastore specific, but will likely refer to the
             name of a previously defined instance in the same ReST
             payload.

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
          },
        ]
      }
    }


HTTP Codes::

    202 - Accepted.
    400 - BadRequest. Server could not understand request.
    403 - Forbidden. Local storage not specified in flavor ID: <ID>.
    403 - Forbidden. A flavor is required for each instance in the cluster.
    404 - Not Found. Flavor <id> not found.
    404 - Not Found. Cluster <id> not found.

cluster-shrink
//////////////

Deletes the specified instances from the cluster.

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
    403 - Forbidden. Instance <instance_id> not in state to be removed.
    404 - Instance <instance_id> not found in cluster <id>.

Configuration
-------------

n/a


Database
--------

n/a


Public API
----------

This change adds new CLI commands cluster-grow and cluster-shrink,
detailed below.  These CLI commands and their corresponding APIs
should be consistent with existing CLI and API usage.


Public API Security
-------------------

No security impacts are expected.


Python API
----------

The following methods will be added to the Clusters class in
the python-troveclient::

  class Clusters:

    def grow(self, cluster, instances)
        """Grow the specified cluster.

        :param cluster: The cluster to grow
        :param instances: JSON describing instances to add
        """

    def shrink(self, cluster, instances)
        """Shrink the specified cluster.

        :param cluster: The cluster to shrink
        :param instances: JSON describing instances to remove
        """


CLI (python-troveclient)
------------------------

cluster-grow
////////////

Basic Grow
++++++++++

Basic Grow would be suitable to databases such as Galera or Cassandra
where all nodes are effectively peers - no special options are
required.

::

    $ trove cluster-grow mycluster --instance flavor=7
    <example output to follow>

    --instance parameter may be specified multiple times.

Generated Request::

    POST /v1.0/<tenant_id>/clusters/<cluster-id>/action
    {
        "grow": [
          {
            "flavorRef": "7",
          }
        ]
    }

Add Master and Slave
++++++++++++++++++++

Master and Slave grow would be suitable for databases such as Redis
which support master/slave replication within a cluster.

::

    $ trove cluster-grow mycluster \
      --instance name=newnode1,type=master,flavor=7 \
      --instance name=newnode2,type=slave,related_to=newnode1,flavor=7

Generated Request::

    POST /v1.0/<tenant_id>/clusters/<cluster-id>/action
    {
        "grow": [
          {
            "name": "newnode1",
            "instance_type": "master",
            "flavorRef": "7"
          },
          {
            "name": "newnode2",
            "instance_type": "slave",
            "related_to": "newnode1",
            "flavorRef": "7 "
          }
        ]
    }

To add a standby node to a node named "node1" in a database such as
Vertica or Redis, a simpler form of the above could be used.

::

    $ trove cluster-grow mycluster \
      --instance type=standby,related_to=node1,flavor=7

Generated Request::

    POST /v1.0/<tenant_id>/clusters/<cluster-id>/action
    {
        "grow": [
          {
            "instance_type": "standby",
            "related_to": "node1",
            "flavorRef": "7 "
          }
        ]
    }

Add Replica Set
+++++++++++++++

This form of Grow Cluster would be used for databases such as MongoDB
which implement growth by shards, in this case called "replica sets".
The example below creates a new query server plus two replica sets of
3 nodes each.

::

    $ trove cluster-grow mycluster \
      --instance name=rs2q,type=query,flavor=7 \
      --instance name=rs2a,type=replica,flavor=7 \
      --instance name=rs2b,type=replica,related_to=rs2a,flavor=7 \
      --instance name=rs2c,type=replica,related_to=rs2b
      --instance name=rs3a,type=replica,flavor=7 \
      --instance name=rs3b,type=replica,related_to=rs3a,flavor=7 \
      --instance name=rs3c,type=replica,related_to=rs3b

Generated Request::

    POST /v1.0/<tenant_id>/clusters/<cluster-id>/action
    {
        "grow": [
          {
            "name": "rs2q",
            "instance_type": "query",
            "flavorRef": "7"
          },
          {
            "name": "rs2a",
            "instance_type": "replica",
            "flavorRef": "7"
          },
          {
            "name": "rs2b",
            "instance_type": "replica",
            "related_to": "rs2a",
            "flavorRef": "7 "
          },
          {
            "name": "rs2c",
            "instance_type": "replica",
            "related_to": "rs2b",
            "flavorRef": "7 "
          },
          {
            "name": "rs3a",
            "instance_type": "replica",
            "flavorRef": "7"
          },
          {
            "name": "rs3b",
            "instance_type": "replica",
            "related_to": "rs3a",
            "flavorRef": "7 "
          },
          {
            "name": "rs3c",
            "instance_type": "replica",
            "related_to": "rs3b",
            "flavorRef": "7 "
          }
        ]
    }

cluster-shrink
//////////////

::

    $ trove cluster-shrink mycluster nodename-1 nodename-2
    <example output to follow>


Internal API
------------

Appropriate methods will be added to the base Cluster Strategy.


Guest Agent
-----------

Appropriate methods will be added to the base Cluster Strategy.

The MongoDB Implementation will be adapted to support both the existing
add-shard functionality, plus the new cluster-grow functionality.


Alternatives
------------

n/a


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Matthew Van Dijk
  Morgan Jones


Milestones
----------

Target Milestone for completion:
  Liberty-3

Work Items
----------

- Implement base cluster-shrink/cluster-grow functionality
- Update MongoDB Clustering implementation to use new APIs


Upgrade Implications
====================

The MongoDB clustering implementation will continue to support the
existing "add-shard" functionality.


Dependencies
============

n/a


Testing
=======

int-tests for clustering functionality is still under consideration.


Documentation Impact
====================

The new cluster-grow and cluster-shrink functionality will need to be
documented.

The MongoDB Datastore documentation will need to be updated to reflect
Mongo's implementation of both the old and new functionality.


References
==========

n/a
