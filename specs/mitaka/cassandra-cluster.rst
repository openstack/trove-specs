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


========================================
Implement cassandra cluster provisioning
========================================

Implement cassandra cluster provisioning.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/cassandra-cluster


Problem Description
===================

Cassandra is by nature a distributed database consisting of 'equal' nodes.
The 'equality' of nodes means that any node in the cluster can receive and
service a request. There are no query routers or configuration servers
like in some other databases (MongoDB).
There are no restrictions on the hardware configuration of individual nodes
(i.e. the nodes may have different flavors).

When a node receives a request (it becomes so called a coordinator for that
request) it uses the partition key (part of the primary key) to compute
which nodes (replicas) contain the requested data (data is distributed based
on the hash of the partition key). It then passes the request to the replicas
and collects the results. Its job is then compose the response to the client.
Each field (value) stored in the database is accompanied by timestamp
(or tombstone marker in case of deleted data). The coordinator uses
these timestamps to compile the most current view of the data into a
result set.
That is why it is absolutely critical for the nodes' clock to be synchronized.

The Cassandra has been designed such that it can survive failure of any given
node(s) and still be available. This was achieved by relaxing the consistency
requirements. Cassandra offers so called eventual consistency.
Both the fault tolerance and consistency can be tuned.
Fault tolerance can be configured on the keyspace level (Replication Factor).
Consistency can be controlled globally or on per-request level
(Consistency Level).

The replication factor determines how many replicas will hold data from a
given keyspace.
Cassandra can group replicas into 'racks'.
A 'rack' is a set of nodes (replicas) that share a common point of failure.
Cassandra always tries to distribute data across multiple racks, so that
failure of one does not render the data inaccessible.

Example:
    Let's have a three-node system (nodes #1, #2 and #3) and a keyspace
    with replication factor (RC) 2. Now let's suppose the user issues an insert
    statement which lands on node #3 (coordinator). The coordinator uses
    the partition key to determine which of the nodes the data belong to,
    say it would be #1. It therefore proceeds to store the data on node #1
    and because RC=2 also on the next node #2.
    Now suppose both node #1 and #2 share a common failure point and are
    placed into a single rack. The coordinator therefore stores the second
    replica on the next available node not in the rack - that is #3 (itself).

Cassandra also has a concept of data centers. Data centers are generally
geographically distant groups of nodes with their own set of racks.
They very much behave like separate clusters.

Example:
    Let's suppose that the example above took place on datacenter DC1, but
    the keyspace in question is also configured to replicate to DC2
    (the replication factor for DC1 does not have to be the same as for DC1).
    The coordinator then fires an asynchronous request to one of the nodes
    in DC2 which then proceeds handling the it in the same way.

Note that it is not uncommon for a keyspace to have replication factor RC=0
for a specific data center - one reason could be legal regulation which require
certain data be stored within a particular geographical region.

Each node is configured with a cluster name. All nodes within a single cluster
must share the same cluster name.
Individual nodes in a cluster exchange so called gossip - basic information
on the cluster's topology. Newly added nodes learn about all the other nodes
the same way. They just need to be provided a set of initial gossip seeds
(already active nodes from within the cluster). It is recommended that
the seed nodes come from multiple racks across all DCs (in case one is down).

All these configurations are stored in the standard 'cassandra.yaml' file
which is already managed by the guest agent [2]_

The node membership (rack/dc) is stored in 'cassandra-rackdc.properties' file
at the same location as the main configuration file.

Proposed Change
===============

This specification proposes the following cluster-related actions:

* create
* grow
* shrink
* delete

Only rack support will be implemented as a part of this patch. All nodes
will be placed into a single DC ('dc1'). The racks will be mapped on the
Availability Zones (AZ) passed from the client. The nodes will be placed into
a single default rack ('rack1') if no AZ is specified.


Create Cluster
--------------

* Provision a requested number of instances.

* Wait for the instances to become active.

* Select the seed nodes.
  They should include at least one node from
  each data center and rack.

* Configure each cluster node with the list of seeds.
  Note that the seed nodes must have the automatic bootstrap *disabled* during
  *initial* startup of a new *empty* cluster.
  Once all nodes are configured, start the seed nodes
  one at a time (automatic bootstrap is disabled at this time)
  followed by the rest of the nodes (automatic bootstrap may be enabled
  as the seed nodes are already running).


* Create the in-database ('os_admin') user via the first node.
  The remaining nodes will replicate in-database
  changes automatically.
  Only update the local authentication file on the
  other nodes.


Grow Cluster
------------

* Provision a requested number of instances.

* Wait for the instances to become active.

* Recompute the seed nodes based on the updated cluster geometry and
  configure each cluster node with the updated list of seeds.

* Retrieve the superuser credentials from one previously existing node
  and save it on the newly added nodes.

* Start any seeds from the added nodes first one at a time followed by the
  rest of the nodes.

* Run nodetool cleanup on each of the previously existing nodes
  to remove the keys that no longer belong to those nodes (they now on belong
  to some of the added nodes).

  Put the node into BLOCKED state first and then initiate the cleanup.
  Restore the node's state once the cleanup finishes. The taskmanager
  can poll for the node state change and proceed to the next node when ready.

  The operation has to be run sequentially on all previously
  existing nodes and can take an excessive amount of time.
  Cleanup can generally be safely postponed for low-usage hours.


Shrink Cluster
--------------

* Recompute the seed nodes based on the updated cluster
  geometry if any of the existing seed nodes was removed.

* Update the list of seeds on remaining nodes if necessary.

* Run nodetool decommission on the removed nodes.
  Cassandra will stream data from decommissioned nodes to the
  remaining ones. Shutdown the database once completed.

* Wait for the removed nodes to go SHUTDOWN.

* Delete decommissioned instances.


Configuration
-------------

The following configuration values will be implemented in the Cassandra
configuration group::

    cfg.BoolOpt('cluster_support', default=True,
                help='Enable clusters to be created and managed.'),
    cfg.StrOpt('api_strategy',
               default='trove.common.strategies.cluster.experimental.'
               'cassandra.api.CassandraAPIStrategy',
               help='Class that implements datastore-specific API logic.'),
    cfg.StrOpt('taskmanager_strategy',
               default='trove.common.strategies.cluster.experimental'
               '.cassandra.taskmanager.CassandraTaskManagerStrategy',
               help='Class that implements datastore-specific task manager '
                    'logic.'),
    cfg.StrOpt('guestagent_strategy',
               default='trove.common.strategies.cluster.experimental'
               '.cassandra.guestagent.CassandraGuestAgentStrategy',
               help='Class that implements datastore-specific Guest Agent API '
                    'logic.'),

Database
--------

None

Public API
----------

None

Public API Security
-------------------

None

Python API
----------

None

CLI (python-troveclient)
------------------------

None

Internal API
------------

The following methods will be implemented in the CassandraGuestAgentAPI::

    def get_data_center(self):
        LOG.debug("Retrieving the data center for node: %s" % self.id)
        return self._call("get_data_center", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def get_rack(self):
        LOG.debug("Retrieving the rack for node: %s" % self.id)
        return self._call("get_rack", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def set_seeds(self, seeds):
        LOG.debug("Configuring the gossip seeds for node: %s" % self.id)
        return self._call("set_seeds", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap, seeds=seeds)

    def get_seeds(self):
        LOG.debug("Retrieving the gossip seeds for node: %s" % self.id)
        return self._call("get_seeds", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def set_auto_bootstrap(self, enabled):
        LOG.debug("Setting the auto-bootstrap to '%s' for node: %s"
                  % (enabled, self.id))
        return self._call("set_auto_bootstrap", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap, enabled=enabled)

    def cluster_complete(self):
        LOG.debug("Sending a setup completion notification for node: %s"
                  % self.id)
        return self._call("cluster_complete", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def node_cleanup_begin(self):
        LOG.debug("Signaling the node to prepare for cleanup: %s" % self.id)
        return self._call("node_cleanup_begin", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def node_cleanup(self):
        LOG.debug("Running cleanup on node: %s" % self.id)
        return self._cast('node_cleanup', self.version_cap)

    def node_decommission(self):
        LOG.debug("Decommission node: %s" % self.id)
        return self._cast("node_decommission", self.version_cap)

    def cluster_secure(self, password):
        LOG.debug("Securing the cluster via node: %s" % self.id)
        return self._call(
            "cluster_secure", guest_api.AGENT_HIGH_TIMEOUT,
            self.version_cap, password=password)

    def get_admin_credentials(self):
        LOG.debug("Retrieving the admin credentials from node: %s" % self.id)
        return self._call("get_admin_credentials", guest_api.AGENT_LOW_TIMEOUT,
                          self.version_cap)

    def store_admin_credentials(self, admin_credentials):
        LOG.debug("Storing the admin credentials on node: %s" % self.id)
        return self._call("store_admin_credentials",
                          guest_api.AGENT_LOW_TIMEOUT, self.version_cap,
                          admin_credentials=admin_credentials)

Guest Agent
-----------

Functionality for writing the 'cassandra-rackdc.properties' file will be
implemented in addition to the above methods.

The node membership (rack/dc) will be included in the cluster_info dictionary
passed into the prepare method.

Alternatives
------------

None


Dashboard Impact (UX)
=====================

Will need to enable Cassandra as a clustering datastore.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Petr Malik <pmalik@tesora.com>

Milestones
----------

Mitaka

Work Items
----------

The work will be delivered as a single commit.


Upgrade Implications
====================

None


Dependencies
============

This implementation heavily depends on work done as a part of:

* blueprint cassandra-database-user-functions [1]_
* blueprint cassandra-configuration-groups [2]_
* blueprint cassandra-backup-restore [3]_


Testing
=======

* Manager unittests will be added where appropriate.

* The scenario tests already cover implemented functionality.


Documentation Impact
====================

Datastore documentation for Cassandra will need to be updated to reflect
clustering support.


References
==========

.. [1] Cassandra user/database implementation review: https://review.openstack.org/#/c/206739/

.. [2] Cassandra configuration review: https://review.openstack.org/#/c/206740/

.. [3] Cassandra backup/restore review: https://review.openstack.org/#/c/206751/


Appendix
========

None
