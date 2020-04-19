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
Implement Couchbase cluster provisioning
========================================

Implement Couchbase cluster provisioning.

Launchpad Blueprint:
https://blueprints.launchpad.net/trove/+spec/couchbase-cluster-support


Problem Description
===================

Couchbase is by nature a distributed database.
Documents are distributed evenly across all nodes based on the hash of the
document key.
There are no query routers or configuration servers like in some other
databases (MongoDB).
Each document may have up to three replicas in addition to the active copy.
What this means is that there will be three extra copies of that data
within the cluster.
Couchbase clients are provided with an updated 'cluster map' which they use to
lookup data.

When a node gets added to the cluster the existing documents are incrementally
redistributed within the cluster (process also known as rebalancing).
Updated cluster maps are continuously provided to the clients.
Any active client connections should not be interrupted throughout the process.

When a node gets removed from the cluster the replicas on the other nodes
are promoted to the active and cluster maps updated so that the clients can
keep serving the requests. The promoted documents are then re-replicated within
the remaining nodes (rebalanced).

See `References`_ section for further details.

Proposed Change
===============

This specification proposes the following cluster-related actions:

* create
* grow
* shrink
* delete
* upgrade

Couchbase imposes cluster wide quota on the memory that get
evenly distributed between node services.
All nodes (including future nodes) need to be able to accommodate
this quota.
We therefore require the cluster to be homogeneous.
The quota size is configurable by 'cluster_ramsize_pc' Trove configuration as
the percentage of the total node RAM.


Create Cluster
--------------

* Provision a requested number of instances while initializing them as
  Couchbase nodes (all nodes receive the same randomly generated Administrative
  credentials from the API).

* Wait for the instances to become active.

* Execute cluster initialization on the first node (coordinator).

* Add the remaining nodes to the cluster via the coordinator node.

* Wait for the cluster rebalance to finish.


Grow Cluster
------------

* Retrieve the current Administrative credentials from the first
  node (coordinator) of the existing cluster.

* Provision and initialize a requested number of instances as Couchbase nodes
  with the current credentials (above).

* Wait for the instances to become active.

* Add the new nodes to the cluster via the coordinator node.

* Wait for the cluster rebalance to finish.


Shrink Cluster
--------------

* Load the removed instances.

* Select one of the remaining nodes and use it as the coordinator.

* Remove the nodes from the cluster via the coordinator.

* Wait for the cluster rebalance to finish.

* Delete decommissioned instances.


Configuration
-------------

The following configuration values will be implemented in the Couchbase
configuration group::

    cfg.BoolOpt('cluster_support', default=True,
                help='Enable clusters to be created and managed.'),
    cfg.StrOpt('api_strategy',
               default='trove.common.strategies.cluster.experimental.'
               'couchbase.api.CouchbaseAPIStrategy',
               help='Class that implements datastore-specific API logic.'),
    cfg.StrOpt('taskmanager_strategy',
               default='trove.common.strategies.cluster.experimental'
               '.couchbase.taskmanager.CouchbaseTaskManagerStrategy',
               help='Class that implements datastore-specific task manager '
                    'logic.'),
    cfg.StrOpt('guestagent_strategy',
               default='trove.common.strategies.cluster.experimental'
               '.couchbase.guestagent.CouchbaseGuestAgentStrategy',
               help='Class that implements datastore-specific Guest Agent API '
                    'logic.'),
    cfg.IntOpt('cluster_ramsize_pc', default=80, min=0, max=80,
               help='Per node RAM quota in for the Data service expressed as a'
               ' percentage of the available memory.'
               ' Minimum of 256MB will be used if the given percentage amounts'
               ' for less.'),

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

None

Guest Agent
-----------

The work will require some preliminary refactoring of the guest manager.
This may also include tasks such that:

 - providing a common framework for executing Couchbase CLI calls
   The guest-agent currently executes only two CLI commands hardcoded in
   'system.py' file. We will need to execute a greater variety of commands.
   This would include CouchbaseAdmin to execute CLI calls and handle results in
   a generic way. It will also facilitate reducing 'system.py'
   which we have been moving away from in other guests as well.
 - making the ramsize quota relative to the node's total RAM
   Couchbase 3 requires a parameter to cluster-init is RAMSIZE quota.
   The valid value is between 256MB and 80% of available RAM.
   Make the default % a Trove variable.
 - using appropriate guestagent models for the Couchbase administrative user
   Couchbase should be using it's own User model rather than relying on
   generic MySQL-object.

The following methods will be implemented in the CouchbaseGuestAgentAPI::

    def initialize_cluster(self):
        LOG.debug("Configuring cluster parameters via node: %s" % self.id)
        self._call("initialize_cluster",
                   guest_api.AGENT_HIGH_TIMEOUT, self.version_cap)

    def get_cluster_password(self):
        LOG.debug("Retrieving cluster password from node: %s" % self.id)
        return self._call("get_cluster_password",
                          guest_api.AGENT_LOW_TIMEOUT, self.version_cap)

    def get_cluster_rebalance_status(self):
        LOG.debug("Retrieving status of current cluster rebalance via node: %s"
                  % self.id)
        return self._call("get_cluster_rebalance_status",
                          guest_api.AGENT_LOW_TIMEOUT, self.version_cap)

    def add_nodes(self, nodes):
        LOG.debug("Adding nodes to the cluster: %s" % self.id)
        self._cast('add_nodes', self.version_cap, nodes=nodes)

    def remove_nodes(self, nodes):
        LOG.debug("Removing nodes from the cluster: %s" % self.id)
        self._cast('remove_nodes', self.version_cap, nodes=nodes)

    def cluster_complete(self):
        LOG.debug("Sending a setup completion notification for node: %s"
                  % self.id)
        return self._call("cluster_complete", guest_api.AGENT_HIGH_TIMEOUT,
                          self.version_cap)

Alternatives
------------

None


Dashboard Impact (UX)
=====================

Will need to enable Couchbase as a clustering datastore.


Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Petr Malik <pmalik@tesora.com>

Milestones
----------

Ocata

Work Items
----------

The preliminary work in the guest manager and cluster strategy itself
may be delivered in two separate commits if it facilitates smoother review
process.


Upgrade Implications
====================

None


Dependencies
============

None


Testing
=======

* Manager unittests will be added where appropriate.

* The scenario tests already cover implemented functionality.


Documentation Impact
====================

Datastore documentation for Couchbase will need to be updated to reflect
clustering support.


References
==========

* Couchbase cluster management: http://docs.couchbase.com/admin/admin/Tasks/cluster-management.html

* Couchbase CLI reference: http://developer.couchbase.com/documentation/server/4.0/cli/cli-intro.html

* Couchbase cluster API: http://docs.couchbase.com/admin/admin/REST/rest-cluster-intro.html


Appendix
========

None
